package org.bigdiff.graph;


import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.neo4j.cypher.javacompat.ExecutionEngine;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * @author Khalid Alharbi
 */
public class GraphMLController {
    private static final Logger logger = LoggerFactory.getLogger(GraphMLController.class);
    private File[] apkDirs;
    private GraphDatabaseService graphDbService;
    private ExecutionEngine executionEngine;
    private String dbLocation;
    private DataStoreTransaction dataStoreTransaction;
    private GraphMLImportWriter graphMLImportWriter = null;

    public GraphMLController(File[] apkDirs, String dbLocationh) {
        this.apkDirs = apkDirs;
        this.dbLocation = dbLocationh;
        try {
            this.graphDbService = new GraphDatabaseFactory()
                    .newEmbeddedDatabaseBuilder(dbLocationh)
                    .newGraphDatabase();
            registerShutdownHook(this.graphDbService);
            this.executionEngine = new ExecutionEngine(this.graphDbService);
            this.dataStoreTransaction = new DataStoreTransaction(this.graphDbService,
                    this.executionEngine);
            if (!this.dataStoreTransaction.isIndexed("App", "name")) {
                logger.info("Creating an index for label: {}, property: {}",
                        "App", "name");
                this.dataStoreTransaction.createIndexFor("App", "name");
            }
            this.graphMLImportWriter = new GraphMLImportWriter(File.createTempFile(
                    "org.bigdiff.ui-graphdb-writer", ".sh").getAbsolutePath());

        } catch (Exception exception) {
            logger.error("Failed to connect to database.", exception);
            System.exit(1);
        }
    }

    public void readGraphML() {
        for (File apkDir : apkDirs) {
            File graphmlDir = new File(apkDir, "ui-graphml");
            if (graphmlDir.exists()) {
                File graphmlFile = FileUtils.listFiles(graphmlDir, new String[]{"graphml"}, false).iterator().next();
                if (graphmlFile != null && graphmlFile.exists()) {
                    logger.info("Reading GraphML file {}", graphmlFile.getAbsolutePath());
                    Map<String, String> appInfo = getAppInfoFromGraphML(graphmlFile);
                    if (appInfo == null) {
                        logger.error("Unable to find app name and version from graphML file {}", graphmlFile.getAbsolutePath());
                        continue;
                    }
                    String packageName = appInfo.get("package");
                    String versionCode = appInfo.get("version_code");
                    if (appExists(packageName, versionCode)) {
                        logger.info("App {}, {} already exists", packageName, versionCode);
                        continue;
                    } else {
                        // write shell command to import-graphml
                        logger.info("Writing import-graphml for app: {}, {}", packageName, versionCode);
                        this.graphMLImportWriter.writeImportCommand(graphmlFile);
                    }
                } else {
                    logger.warn("{} no .graphml file found in {}", graphmlDir.getAbsolutePath());
                }
            } else {
                logger.warn("{} no such directory {}", graphmlDir.getAbsolutePath());
            }
        }
        // finally close the bash script
        this.graphMLImportWriter.closeWrite();
        logger.info("Import commands have been written successfully at: {} \nTo start importing, use sh {}",
                graphMLImportWriter.getFilePathName(), graphMLImportWriter.getFilePathName());
    }

    private boolean appExists(String packageName, String versionCode) {
        ArrayList<Node> appNodes = this.dataStoreTransaction.findNode("App", "name", packageName);
        if (appNodes == null || appNodes.size() == 0) {
            return false;
        }
        for(int i=0; i<appNodes.size(); i++) {
            Node appNode = appNodes.get(i);
            try (Transaction tx = this.graphDbService.beginTx()) {
                if (versionCode.equals(appNode.getProperty("version_code").toString())) {
                    return true;
                }
                tx.success();
            }
        }
        return false;
    }

    private static Map<String, String> getAppInfoFromGraphML(File graphMLFile) {
        Map<String, String> appInfo = null;
        try {
            String fileName = FilenameUtils.getBaseName(graphMLFile.getAbsolutePath());
            String packageName = fileName.substring(0, fileName.lastIndexOf('-'));
            String version_code = fileName.substring(fileName.lastIndexOf('-') + 1,
                    fileName.length());
            appInfo = new HashMap<>();
            appInfo.put("package", packageName);
            appInfo.put("version_code", version_code);
        } catch (IndexOutOfBoundsException e) {
            logger.error("Failed to extract file name from the GraphMl file. The file name must be named " +
                    "using the following scheme: packageName-versionCode.graphml");
        }
        return appInfo;
    }

    private void registerShutdownHook(final GraphDatabaseService graphDb) {
        // Registers a shutdown hook for the Neo4j instance so that it
        // shuts down nicely when the VM exits (even if you "Ctrl-C" the
        // running application).
        Runtime.getRuntime().addShutdownHook(new Thread() {
            @Override
            public void run() {
                graphDb.shutdown();
            }
        });
    }

}
