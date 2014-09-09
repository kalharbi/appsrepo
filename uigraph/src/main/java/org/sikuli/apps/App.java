package org.sikuli.apps;

import java.io.File;
import java.util.HashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import org.sikuli.apps.utils.Constants;
import org.sikuli.apps.utils.PackageInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class App {
	private final static Logger logger = LoggerFactory.getLogger(App.class);

	public void startUIGraph(File[] apkDirs) {
		long startTime = System.currentTimeMillis();

		final int numberOfCores = Runtime.getRuntime().availableProcessors();
		final double blockingCoefficient = 0.4;
		final int poolSize = Constants.NTHREADS > 0 ? Constants.NTHREADS
				: (int) (numberOfCores / (1 - blockingCoefficient));
		logger.info("Number of Cores available: {}", numberOfCores);
		logger.info("Pool size: {}", poolSize);

		final ExecutorService parserExecutor = Executors
				.newFixedThreadPool(poolSize); // Parser Executor
		UIGraphController uiGraphController = new UIGraphController();
		uiGraphController.setup();
		int i = 1;
		for (File apkDir : apkDirs) {
			HashMap<String, String> appInfo = getAppInfo(apkDir);
			String packageName = appInfo.get("package");
			String versionCode =appInfo.get("versionCode");
			String versionName = appInfo.get("versionName");
			if(packageName!=null && versionCode!=null && versionName !=null){
				logger.info("{} - Parsing package {}, version code:{}", i, packageName, versionCode);
				uiGraphController.startUIGraph(apkDir, packageName, versionCode, versionName);
			}
			else{
				logger.error("Missing package name and version info for {}", apkDir);
			}
			i++;
		}
		uiGraphController.shutdown();
		shutdownAndAwaitTermination(parserExecutor);
		printExecutionTime(startTime);
	}
	
	private HashMap<String, String> getAppInfo(File apkDir){
		HashMap<String, String> appInfo = null;
		String packageName = PackageInfo.getPackageNameFromManifest(new File(apkDir, "AndroidManifest.xml"));
		HashMap<String, String> appVersion = PackageInfo.getVersionFromYAMLFile(new File(apkDir, "apktool.yml"));
		if(appVersion==null){
			appVersion = PackageInfo.getVersionFromManifest(new File(apkDir, "AndroidManifest.xml"));
			if(appVersion!=null){
				appInfo = new HashMap<String, String>();
				appInfo.put("package", packageName);
				appInfo.put("versionCode", appVersion.get("versionCode"));
				appInfo.put("versionName", appVersion.get("versionName"));
			}
		}
		else{
			appInfo = new HashMap<String, String>();
			appInfo.put("package", packageName);
			appInfo.put("versionCode", appVersion.get("versionCode"));
			appInfo.put("versionName", appVersion.get("versionName"));
		}
		return appInfo;
	}
	// http://docs.oracle.com/javase/6/docs/api/java/util/concurrent/ExecutorService.html
	private void shutdownAndAwaitTermination(ExecutorService pool) {
		pool.shutdown(); // Disable new tasks from being submitted
		try {
			// Wait for existing tasks to terminate
			if (!pool.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS)) {
				pool.shutdownNow(); // Cancel currently executing tasks
				// Wait a while for tasks to respond to being cancelled
				if (!pool.awaitTermination(60, TimeUnit.SECONDS))
					logger.error("Something went wrong! The thread pool did not terminate");
			}
		} catch (InterruptedException ie) {
			// (Re-)Cancel if current thread also interrupted
			pool.shutdownNow();
			// Preserve interrupt status
			Thread.currentThread().interrupt();
		}
	}

	private void printExecutionTime(long startTime) {
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

	public static void main(String[] args) {
		App app = new App();
		CommandLineTool cmd = new CommandLineTool();
		cmd.parseCommandLine(args);
		File[] apkDirs = cmd.getApkDirs();
		if (apkDirs != null && apkDirs.length > 0) {
			app.startUIGraph(apkDirs);
		}
	}

}
