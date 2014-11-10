/**
 Khalid
 */
package org.bigdiff;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.rolling.RollingFileAppender;
import ch.qos.logback.core.rolling.TimeBasedRollingPolicy;
import com.beust.jcommander.JCommander;
import com.beust.jcommander.ParameterException;
import org.apache.commons.io.FileUtils;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.net.URLDecoder;

public class CommandLineTool {
    private final static LoggerContext loggerContext = (LoggerContext) LoggerFactory
            .getILoggerFactory();
    private static final String applicationName = "ui-graphml";
    private static final String versionNumber = CommandLineTool.class
            .getPackage().getImplementationVersion();
    private static final String NEW_LINE = System.getProperty("line.separator");
    private static final String header = " -- Android UI GraphML writer: A tool for representing" + NEW_LINE +
            " Android apps' user interfaces in a GraphML file format, a common " + NEW_LINE
            + "XML-based representation of a graph.";

    private File[] apkDirs = null;

    File logFile = null;

    /**
     * Parse command-line arguments.
     *
     * @param args Command-line arguments
     */
    public void parseCommandLine(final String[] args) {
        CommandLineParameters cmdParameters = new CommandLineParameters();
        JCommander jCommander = new JCommander(cmdParameters);
        jCommander.setProgramName(applicationName);
        jCommander.setAcceptUnknownOptions(false);
        try {
            logFile = new File(URLDecoder.decode(CommandLineTool.class
                    .getProtectionDomain().getCodeSource().getLocation()
                    .getPath(), "UTF-8"), "UI-GraphML-Log-" + System.nanoTime()
                    + ".log");
            jCommander.parse(args);
            if (cmdParameters.help) {
                printUsage(jCommander);
                System.exit(0);
            } else if (cmdParameters.version) {
                String versionMsg = applicationName + " -- version "
                        + versionNumber + NEW_LINE;
                System.out.write(versionMsg.getBytes());
                System.exit(0);
            }
            if (cmdParameters.logFile != null) {
                if (!cmdParameters.logFile.isDirectory()) {
                    throw new ParameterException("The path to the log directory is missing or does not exist.");
                }
                logFile = new File(cmdParameters.logFile, "ui-graphML-" + System.currentTimeMillis() + ".log");
            }
            if (cmdParameters.parameters == null || cmdParameters.parameters.size() != 1) {
                throw new ParameterException("The directory path of unpacked apk file(s) is not specified.");
            }
            // Pass the directory path command line argument.
            doInput(cmdParameters.parameters.get(0));
            // setup file logger.
            setupLogger(logFile);
        } catch (IOException exception) {
            System.out.println("Error: " + exception.getMessage());
            jCommander.usage();
        } catch (ParameterException exception) {
            System.out.println("Error: " + exception.getMessage());
            jCommander.usage();
        }
    }

    //TODO: Fix log file
    private void setupLogger(File logFile) {
        RollingFileAppender<ILoggingEvent> rollingFileAppender = new RollingFileAppender<ILoggingEvent>();
        rollingFileAppender.setContext(loggerContext);
        rollingFileAppender.setName("timestamp");
        rollingFileAppender.setFile(logFile.getAbsolutePath());
        @SuppressWarnings("rawtypes")
        TimeBasedRollingPolicy rollingPolicy = new TimeBasedRollingPolicy();
        rollingPolicy.setContext(loggerContext);
        rollingPolicy.setMaxHistory(7);
        rollingPolicy.setParent(rollingFileAppender);
        rollingPolicy.setFileNamePattern(loggerContext.getName() + ".%d{yyyy-MM-dd}.log");
        rollingPolicy.start();

        PatternLayoutEncoder patternLayoutEncoder = new PatternLayoutEncoder();
        patternLayoutEncoder.setContext(loggerContext);
        patternLayoutEncoder.setPattern("%date %level %msg%n");
        patternLayoutEncoder.start();

        rollingFileAppender.setEncoder(patternLayoutEncoder);
        rollingFileAppender.setRollingPolicy(rollingPolicy);
        rollingFileAppender.start();
        Logger logger = loggerContext.getLogger("CommandLineTool");
        logger.addAppender(rollingFileAppender);

    }

    private void doInput(String inputDirPath) {
        if (inputDirPath != null) {
            File inputDir = new File(inputDirPath);
            if (!inputDir.exists()) {
                System.err.println("Error: input directory does not exist. "
                        + inputDirPath);
                System.exit(2);
            }
            if (inputDir.isDirectory()) {
                // if the input directory contains a single unpacked apk file.
                if (new File(inputDir, "AndroidManifest.xml").exists()) {
                    this.apkDirs = new File[]{inputDir};
                } else {
                    // if the input directory contains multiple unpacked apk
                    // files.
                    this.apkDirs = inputDir.listFiles(new FilenameFilter() {
                        public boolean accept(File dir, String name) {
                            try {
                                if (FileUtils.directoryContains(dir, new File(
                                        dir, name))) {
                                    return new File(dir, name).isDirectory();
                                }
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                            return false;
                        }
                    });
                }
            }

            if (this.apkDirs == null || this.apkDirs.length < 1) {
                System.err
                        .println("Error: Unable to find unpacked apk file(s) in "
                                + inputDirPath);
                System.exit(2);
            }
        }
    }

    /**
     * print usage information
     */
    public void printUsage(final JCommander jCommander) {
        System.out.print(applicationName);
        System.out.println(header);
        System.out.println(NEW_LINE);
        jCommander.usage();
        System.out.println(NEW_LINE);
    }

    public File[] getApkDirs() {
        return apkDirs;
    }

    public String getLogFilePath() {
        /*if(this.logFile !=null){
            return this.logFile.getAbsolutePath();
        }*/
        return "~/logs";
    }

}

