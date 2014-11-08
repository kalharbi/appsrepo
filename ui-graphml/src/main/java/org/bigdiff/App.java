package org.bigdiff;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.concurrent.TimeUnit;

/**
 * Main/Driver Class
 */
public class App {
    private static final Logger logger = LoggerFactory.getLogger(App.class);

    public static void main(String[] args) {
        CommandLineTool cmd = new CommandLineTool();
        cmd.parseCommandLine(args);
        File[] apkDirs = cmd.getApkDirs();
        if (apkDirs == null || apkDirs.length == 0) {
            logger.error("No unpacked apk files found." +
                    " Please specify the directory that contains unpacked apk files.");
            return;
        }
        long startTime = System.currentTimeMillis();
        AppLayoutsController appInfoController = new AppLayoutsController(apkDirs);
        appInfoController.createGraphML();
        logger.info("Error logs have been saved at: {}", cmd.getLogFilePath());
        printExecutionTime(startTime);
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
