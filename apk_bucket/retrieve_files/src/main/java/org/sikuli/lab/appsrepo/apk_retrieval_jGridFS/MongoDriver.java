/**
Khalid
 */
package org.sikuli.lab.appsrepo.apk_retrieval_jGridFS;

import java.io.File;
import java.io.IOException;
import java.net.UnknownHostException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.MongoClient;
import com.mongodb.gridfs.GridFS;
import com.mongodb.gridfs.GridFSDBFile;

public class MongoDriver {

	private final static Logger logger = LoggerFactory
			.getLogger(MongoDriver.class);
	private File targetDirectory = null;
	private GridFS gridFS = null;

	public MongoDriver(String localhost, int port, String dbName,
			String collectionName, File targetDirectory) {
		try {
			MongoClient mongoClient = new MongoClient(localhost, 27017);
			DB db = mongoClient.getDB(dbName);
			this.gridFS = new GridFS(db, "apk");
		} catch (UnknownHostException e) {
			logger.error("{}", e);
			System.exit(1);
		}
		this.targetDirectory = targetDirectory;
	}

	/**
	 * Find the APK file for the given package name and version code, and save
	 * the file into this target directory.
	 * 
	 * @param packageName
	 *            Android package name.
	 * @param versionCode
	 *            Android version code.
	 * 
	 */
	public void findUsingPackageName(String packageName, String versionCode) {

		BasicDBObject query = new BasicDBObject("metadata.n", packageName)
				.append("metadata.verc", versionCode);

		GridFSDBFile apkFile = this.gridFS.findOne(query);
		if (apkFile == null) {
			logger.error(
					"Could not find apk file for package name:{}, version code:{}",
					packageName, versionCode);
			return;
		}
		logger.info("Found apk file for package name: {}, version code: {}", apkFile.getMetaData()
				.get("n").toString(), apkFile.getMetaData().get("verc")
				.toString());

		File file = new File(this.targetDirectory, packageName + "-"
				+ versionCode + ".apk");
		try {
			apkFile.writeTo(file);
		} catch (IOException e) {
			logger.error(
					"Failed to copy APK file for package:{}, version code:{}. Error message:{}",
					packageName, versionCode, e);
		}
	}

}
