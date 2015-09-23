var Promise = require("bluebird");
var using = Promise.using;
var _ = require("lodash");
var fs = Promise.promisifyAll(require("fs"));
var mongodb = Promise.promisifyAll(require("mongodb"));
var MongoClient = mongodb.MongoClient;
var MongoError = mongodb.MongoError;
var directory = "/Users/khalid/android-apps/listing";
var config = require("./config");
var sourceConfig = config.sourceDB;
var targetConfig = config.targetDB;
var targetUrl = "mongodb://" + targetConfig.host + ":" + targetConfig.port + "/" + targetConfig.db;
var sourceUrl = "mongodb://" + sourceConfig.host + ":" + sourceConfig.port + "/" + sourceConfig.db;

function getConnection(url) {
  return MongoClient.connectAsync(url);
}

function insert(sourceDB, targetDB) {
  return fs.readdirAsync(directory)
    .map(function(filename) {
      return fs.readFileAsync(directory + "/" + filename, "utf8")
        .then(function(content) {
          var app = JSON.parse(content);
          var id = app['n'] + "-" + app['verc'];
          if (_.isEmpty(id)) {
            throw new Error(filename + " no app name is available.");
          }
          app['id'] = id;
          return app
        })
        .then(function(app){
          return Promise.props({
            app:app,
            doc: sourceDB.collection(sourceConfig.collection).findOne({id: app.id})});
        })
        .then(function(result){
          if(_.isEmpty(result.doc) || _.isEmpty(result.doc.vern)){
            throw new Error(filename + " failed to find version name.");
          }
          result.app['vern'] = result.doc.vern;
          return result.app
        })
        .then(function(app) {
          return targetDB.collection(targetConfig.collection)
            .insertOne(app)
        })
        .then(function(r) {
          console.log("A new document has been inserted for " + r);
        })
        .catch(MongoError, function(e) {
          console.error("Failed to insert app ", e.message);
        })
        .catch(function(e) {
          console.error("Unexpected error", e)
        })
    })
    .then(function() {
      console.log("All done");
      sourceDB.close();
      targetDB.close();
    });
}

function main() {
  using(getConnection(sourceUrl), getConnection(targetUrl), function(
    sourceConnection, targetConnection) {
    insert(sourceConnection, targetConnection);
  })
}

main();
