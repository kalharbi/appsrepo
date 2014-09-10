/**
Khalid
 */
package org.sikuli.apps;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.URLDecoder;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.io.FileUtils;
import org.sikuli.apps.utils.Constants;
import org.slf4j.LoggerFactory;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.rolling.RollingFileAppender;
import ch.qos.logback.core.rolling.TimeBasedRollingPolicy;

public class CommandLineTool {
	private final static LoggerContext loggerContext = (LoggerContext) LoggerFactory
			.getILoggerFactory();
	private static final String applicationName = "uiGraph";
	private static final String versionNumber = CommandLineTool.class
			.getPackage().getImplementationVersion();
	private static final String commandLineSyntax = "java -jar "
			+ applicationName + "-" + versionNumber + ".jar <unpacked_apks_dir>";

	private static final String NEW_LINE = System.getProperty("line.separator");
	private File[] apkDirs = null;

	/**
	 * Parse the command-line arguments as GNU-style long option (one word long
	 * option).
	 * 
	 * @param args
	 *            Command-line arguments
	 * @return the location of the .pptx file
	 */
	public void parseCommandLine(final String[] args) {
		try {
			final CommandLineParser parser = new GnuParser();
			final Options posixOptions = getCommandLineOptions();
			CommandLine cmd;
			cmd = parser.parse(posixOptions, args);
			File logFile = new File(URLDecoder.decode(CommandLineTool.class
					.getProtectionDomain().getCodeSource().getLocation()
					.getPath(), "UTF-8"), "uiGraph-log-" + System.nanoTime()
					+ ".log");

			if (cmd.hasOption("help")) {
				printHelp(getCommandLineOptions());
				System.exit(0);
			} else if (cmd.hasOption("version")) {
				String versionMsg = applicationName + " -- version "
						+ versionNumber + NEW_LINE;
				System.out.write(versionMsg.getBytes());
				System.exit(0);
			}
			if (cmd.hasOption("log")) {
				logFile = new File(cmd.getOptionValue("log"));
			}
			if (cmd.hasOption("nthreads")) {
				int nthreads = Integer.parseInt(cmd.getOptionValue("nthreads"));
				if (nthreads > 0) {
					Constants.NTHREADS = nthreads;
				} else {
					String errorMessage = "Invalid number of threads"
							+ NEW_LINE;
					System.out.write(errorMessage.getBytes());
				}
			}
			if (cmd.hasOption("dbpath")) {
				Constants.DB_PATH = cmd.getOptionValue("dbpath");
			}
			if (cmd.hasOption("neo4jpath")) {
				Constants.NEO_HOME = cmd.getOptionValue("neo4jpath");
			}
			// get directory path argument.
			final String[] remainingArguments = cmd.getArgs();
			if (remainingArguments == null || remainingArguments.length != 1) {
				throw new Exception("Directory path is not specified.");
			}
			doInput(remainingArguments[0]);
			// setup file logger.
			setupLogger(logFile);
		} catch (Exception exception) {
			printUsage(applicationName, getCommandLineOptions(), System.out);
			displayBlankLine();
		}
	}

	private void setupLogger(File logFile) {
		System.out.println(logFile.getAbsolutePath());
		RollingFileAppender<ILoggingEvent> rollingFileAppender = new RollingFileAppender<ILoggingEvent>();
		rollingFileAppender.setContext(loggerContext);
		rollingFileAppender.setFile(logFile.getAbsolutePath());
		@SuppressWarnings("rawtypes")
		TimeBasedRollingPolicy rollingPolicy = new TimeBasedRollingPolicy();
		rollingPolicy.setContext(loggerContext);
		rollingPolicy.setMaxHistory(7);
		rollingPolicy.setParent(rollingFileAppender);
		rollingPolicy.setFileNamePattern("uiGraph.%d{yyyy-MM-dd}.log");
		rollingPolicy.start();

		PatternLayoutEncoder patternLayoutEncoder = new PatternLayoutEncoder();
		patternLayoutEncoder.setContext(loggerContext);
		patternLayoutEncoder.setPattern("%date %level %msg%n");
		patternLayoutEncoder.start();

		rollingFileAppender.setEncoder(patternLayoutEncoder);
		rollingFileAppender.setRollingPolicy(rollingPolicy);
		rollingFileAppender.start();
		Logger logger = loggerContext.getLogger("LogFile");
		logger.setLevel(Level.INFO);
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
					this.apkDirs = new File[] { inputDir };
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

	@SuppressWarnings("static-access")
	private Options getCommandLineOptions() {
		final Options gnuOptions = new Options();

		Option helpOption = new Option("help", "print help info.");

		Option versionOption = new Option("version",
				"print the version number.");

		Option logFileOption = OptionBuilder.withArgName("FILE").hasArg()
				.withDescription("Write logs to FILE.").withLongOpt("log")
				.create("l");
		
		Option dbpathOption = OptionBuilder.withArgName("DIR").hasArg()
				.withDescription("The database path.").withLongOpt("DIR")
				.create("d");
		
		Option neo4jpathOption = OptionBuilder.withArgName("DIR").hasArg()
				.withDescription("neo4j HOME directory.").withLongOpt("DIR")
				.create("n");

		Option workerThreadsOption = OptionBuilder
				.withArgName("nthreads")
				.hasArg()
				.withDescription(
						"Set the number of threads to handle extracting UI elements and storing them in the GraphDB."
								+ "The default is to allocate an optimal number of threads relative to the available CPU cores.")
				.withLongOpt("thread").create("t");

		gnuOptions.addOption(helpOption);
		gnuOptions.addOption(versionOption);
		gnuOptions.addOption(logFileOption);
		gnuOptions.addOption(dbpathOption);
		gnuOptions.addOption(neo4jpathOption);
		gnuOptions.addOption(workerThreadsOption);

		return gnuOptions;
	}

	/**
	 * print usage information to provided OutputStream
	 * 
	 * @param applicationName
	 *            Name of application to list in usage
	 * @param options
	 *            Command-line options to be part of usage
	 * @param out
	 *            OutputStream to which to write the usage information
	 */
	public void printUsage(final String applicationName, final Options options,
			final OutputStream out) {
		final PrintWriter writer = new PrintWriter(out);
		final HelpFormatter usageFormatter = new HelpFormatter();
		usageFormatter.printUsage(writer, 120, commandLineSyntax, options);
		writer.flush();
	}

	private void showTextHeader(final OutputStream out) {
		String textHeader = applicationName
				+ " -- A tool for storing Android UI elements in a Graph database.";
		try {
			out.write(textHeader.getBytes());
		} catch (IOException ioEx) {
			System.out.println(textHeader);
		}
	}

	/**
	 * Write command-line tool help
	 * 
	 * @param options
	 *            the possible options for the command-line
	 */
	private void printHelp(final Options options) {
		showTextHeader(System.out);
		displayBlankLine();
		HelpFormatter formatter = new HelpFormatter();
		formatter.printHelp(commandLineSyntax, options);
	}

	private void displayBlankLine() {
		try {
			System.out.write(NEW_LINE.getBytes());
		} catch (IOException e) {
			System.out.println();
		}
	}

	public File[] getApkDirs() {
		return apkDirs;
	}

}
