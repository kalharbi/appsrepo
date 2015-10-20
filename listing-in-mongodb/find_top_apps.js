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

var minDownloadCount = 500000000;

var dbUrl = "mongodb://" + host + ":" + port + "/" + dbName;

function getConnection(url) {
  return MongoClient.connectAsync(url);
}

function find(dbConnection) {
  var collection = dbConnection.collection('listings');
  collection.find({dct:{"$gt": minDownloadCount}},{n:1})
    .toArray()
    .then(function(docs) {
      var returnedApps = _.pluck(docs, 'n');
      var uniqueApps = _.unique(returnedApps);
      uniqueApps.forEach(function(app, index) {
        console.log(app);
      })
    })
    .then(function(){
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
