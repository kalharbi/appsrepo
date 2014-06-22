package org.sikuli.lab.appsrepo.apk_retrieval_jGridFS;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import org.sikuli.lab.appsrepo.apk_retrieval_jGridFS.cmd.CommandLineTool;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {
	private final static Logger logger = LoggerFactory.getLogger(App.class);

	public static void main(String[] args) {
		long startTime = System.currentTimeMillis();
		CommandLineTool cmd = new CommandLineTool();
		cmd.parseCommandLine(args);
		File targetDirectory = cmd.getTargetDirectory();
		File packageListFile = cmd.getPackageListFile();
		String packageName = cmd.getPackageName();
		String versionCode = cmd.getVersionCode();
		MongoDriver mongoDriver = new MongoDriver("localhost", 27017, "apps",
				"apk", targetDirectory);

		if (packageListFile != null) {
			BufferedReader br;
			try {
				br = new BufferedReader(new FileReader(packageListFile));
				// skip header
				br.readLine();
				// read line by line
				String line;
				while ((line = br.readLine()) != null) {
					String[] values = line.split(",");
					packageName = values[0];
					versionCode = values[1];
					mongoDriver.findUsingPackageName(packageName, versionCode);
				}
				logger.info("Logs are saved at: ~/logs");
				printExecutionTime(startTime);
			} catch (FileNotFoundException e) {
				logger.error("{}", e);
			} catch (IOException e) {
				logger.error("{}", e);
			}
		} else if (packageName != null && versionCode != null) {
			mongoDriver.findUsingPackageName(packageName, versionCode);
			logger.info("Logs are saved at: ~/logs");
			printExecutionTime(startTime);
		}
	}

	private static void printExecutionTime(long startTime) {
		long endTime = System.currentTimeMillis();
		long elapsedTime = endTime - startTime;
		long hr = TimeUnit.MILLISECONDS.toHours(elapsedTime);
		long min = TimeUnit.MILLISECONDS.toMinutes(elapsedTime
				- TimeUnit.HOURS.toMillis(hr));
		long sec = TimeUnit.MILLISECONDS.toSeconds(elapsedTime
				- TimeUnit.HOURS.toMillis(hr) - TimeUnit.MINUTES.toMillis(min));
		long ms = TimeUnit.MILLISECONDS.toMillis(elapsedTime
				- TimeUnit.HOURS.toMillis(hr) - TimeUnit.MINUTES.toMillis(min)
				- TimeUnit.SECONDS.toMillis(sec));
		String formattedTime = String.format("%02d:%02d:%02d.%02d", hr, min,
				sec, ms);
		logger.info("Finished after {}", formattedTime);
	}
}
