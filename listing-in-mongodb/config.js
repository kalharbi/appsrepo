// The MongoDB collection to which the JSON files are stored.
var targetDB = {
  host: "localhost",
  port: 27017,
  user: "",
  pw: "",
  db: "apps",
  collection: "listings_test"
}

// The MongoDB collection that contains the vern field.
// vern field is not avilable in the JSON files, so we need to obtain it from
// another MongoDB collection
var sourceDB = {
  host: "localhost",
  port: 27017,
  user: "",
  pw: "",
  db: "apps",
  collection: "apk_paths"
}

// The directory that contains the JSON files.
var DATASET_PATH = "/Users/khalid/android-apps/listing";

module.exports = {
  targetDB: targetDB,
  sourceDB: sourceDB,
  DATASET_PATH: DATASET_PATH
};
