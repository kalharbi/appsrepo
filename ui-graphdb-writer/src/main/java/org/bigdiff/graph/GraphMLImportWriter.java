package org.bigdiff.graph;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

/**
 * Write import graphml commands in bash shell script file, so it can be imported into
 * neo4j using the import-graphml tool o the neo4j-shell tools.
 *
 * @author Khalid Alharbi
 */
public class GraphMLImportWriter {

    private final static Logger logger = LoggerFactory
            .getLogger(GraphMLImportWriter.class);
    private String filePathName;
    private String bashFileHeader = "#!/bin/bash" + System.lineSeparator() +
            "neo4j-shell <<EOF";
    private String bashFileFooter = "exit" + System.lineSeparator() + "EOF";
    private Writer writer = null;

    public GraphMLImportWriter(String filePathName) {
        this.filePathName = filePathName;
        String encoding = "utf-8";
        try {
            writer = new BufferedWriter(new OutputStreamWriter(
                    new FileOutputStream(this.filePathName, false), encoding));
            writer.write(this.bashFileHeader + System.lineSeparator());
        } catch (UnsupportedEncodingException e) {
            logger.error("encoding {} is not supported, {}", encoding, e);
        } catch (FileNotFoundException e) {
            logger.error("File Not found {}, {}", filePathName, e);
        } catch (IOException e) {
            logger.error("IO Exception while writing to file: {}, {}",
                    filePathName, e);
        }
    }

    public void writeImportCommand(File graphMLFile) {
        try {
            if (graphMLFile != null && graphMLFile.exists()) {
                writer.write("import-graphml -i " + graphMLFile.getAbsolutePath() + " -t" +
                        System.lineSeparator());
            }
        } catch (IOException e) {
            logger.error("IO Exception while writing to file: {}, {}",
                    filePathName, e);
        }
    }

    public void closeWrite() {
        try {
            writer.write(bashFileFooter + System.lineSeparator());
            writer.close();
        } catch (IOException e) {
            logger.error(
                    "Failed to writer or close the writing stream of: {}, {}",
                    filePathName, e);
        }
    }

    public String getFilePathName() {
        return filePathName;
    }
}
