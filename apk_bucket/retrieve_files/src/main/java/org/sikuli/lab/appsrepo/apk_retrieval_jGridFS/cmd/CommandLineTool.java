package org.sikuli.lab.appsrepo.apk_retrieval_jGridFS.cmd;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

public class CommandLineTool {
	private static final String applicationName = "apk_retrieval_jGridFS";
	private static final String versionNumber = CommandLineTool.class
			.getPackage().getImplementationVersion();
	private static final String commandLineSyntax = "java -jar "
			+ applicationName
			+ "-"
			+ versionNumber
			+ ".jar"
			+ "{ {package_name version_code} | package_list_file } target_directory [OPTIONS]";

	private static final String NEW_LINE = System.getProperty("line.separator");
	private File targetDirectory = null;
	private String packageName = null;
	private String versionCode = null;
	private File packageListFile = null;

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

			if (cmd.hasOption("help")) {
				printHelp(getCommandLineOptions());
				System.exit(0);
			} else if (cmd.hasOption("version")) {
				String versionMsg = applicationName + " -- version "
						+ versionNumber + NEW_LINE;
				System.out.write(versionMsg.getBytes());
				System.exit(0);
			}
			// get directory path argument.
			final String[] remainingArguments = cmd.getArgs();
			if (remainingArguments == null) {
				throw new Exception("Missing arguments.");
			}
			if (!(remainingArguments.length == 2 || remainingArguments.length == 3)) {
				throw new Exception("Invalide number of arguments.");
			}
			processArgs(remainingArguments);
		} catch (Exception exception) {
			printUsage(applicationName, getCommandLineOptions(), System.out);
			displayBlankLine();
		}
	}

	private void processArgs(String[] args) {
		if (args.length == 3) {
			String packageName = args[0];
			String versionCode = args[1];
			File targetDirectory = new File(args[2]);
			if (!targetDirectory.exists() || !targetDirectory.isDirectory()) {
				System.err.println("No such Directory. " + args[2]);
				System.exit(2);
			}
			setPackageName(packageName);
			setVersionCode(versionCode);
			setTargetDirectory(targetDirectory);
		} else if (args.length == 2) {
			File packageListFile = new File(args[0]);
			if (!packageListFile.exists()) {
				System.err.println("No such File. " + args[0]);
				System.exit(2);
			}
			File targetDirectory = new File(args[1]);
			if (!targetDirectory.exists() || !targetDirectory.isDirectory()) {
				System.err.println("No such Directory. " + args[1]);
				System.exit(2);
			}
			setPackageListFile(packageListFile);
			setTargetDirectory(targetDirectory);

		} else {
			System.err.println("Invalide number of arguments.");
			System.exit(2);
		}
	}

	private static Options getCommandLineOptions() {
		final Options gnuOptions = new Options();

		Option helpOption = new Option("help", "print help and exit.");

		Option versionOption = new Option("version",
				"print the version number.");

		gnuOptions.addOption(helpOption);
		gnuOptions.addOption(versionOption);

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
				+ " -- A tool for retrieving APK files from MongoDB GridFS.";
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

	public File getTargetDirectory() {
		return targetDirectory;
	}

	public void setTargetDirectory(File targetDirectory) {
		this.targetDirectory = targetDirectory;
	}

	public String getPackageName() {
		return packageName;
	}

	public void setPackageName(String packageName) {
		this.packageName = packageName;
	}

	public String getVersionCode() {
		return versionCode;
	}

	public void setVersionCode(String versionCode) {
		this.versionCode = versionCode;
	}

	public File getPackageListFile() {
		return packageListFile;
	}

	public void setPackageListFile(File packageListFile) {
		this.packageListFile = packageListFile;
	}
}
