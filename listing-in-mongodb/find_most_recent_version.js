var Promise = require("bluebird");
var using = Promise.using;
var _ = require("lodash");
var fs = require("fs");
var path = require("path");
var mongodb = Promise.promisifyAll(require("mongodb"));
var MongoClient = mongodb.MongoClient;
var MongoError = mongodb.MongoError;


// DB Connection info
var host = "localhost";
var port = 27017;
var dbName = "apps";
var collection = "listings";
var packageNameFile = "/Users/khalid/git/appsrepo/listing-in-mongodb/top_apps.txt";

var minDownloadCount = 1000000;

var dbUrl = "mongodb://" + host + ":" + port + "/" + dbName;

function getConnection(url) {
  return MongoClient.connectAsync(url);
}

function findMaxVersionNumber(collection, packageName) {
  return collection.find({n: packageName},{verc: 1})
    .toArray()
    .then(function(docs) {
      var versions = _.pluck(docs, "verc");
      var maxVersion = _.max(versions);
      return {
        n: packageName,
        verc: maxVersion
      };
    });
  }

  function find(dbConnection) {
    var packageNames = _.compact(fs.readFileSync(packageNameFile, 'utf8').split('\n'));
    var collection = dbConnection.collection('listings');
    Promise.map(packageNames, function(packageName) {
        return findMaxVersionNumber(collection, packageName)
          .catch(function(e) {
            e.packageName = packageName;
            throw e;
          })
      })
      .then(function(apps) {
        _.forEach(apps, function(app){
          console.log(app.n + "-" + app.verc);
        });
        dbConnection.close();
      })
      .catch(MongoError, function(e) {
        console.error("Failed to insert app ", e.message);
      })
      .catch(function(e) {
        console.error("Unexpected error", e)
      })
  }

  function main() {
    using(getConnection(dbUrl), function(dbConnection) {
      return find(dbConnection);
    });
  }

  main();
