package org.bigdiff;

import com.google.common.base.Strings;
import org.apache.commons.io.FileUtils;
import org.bigdiff.graphmlwriters.GraphMLWriter;
import org.bigdiff.parsers.LayoutParser;
import org.bigdiff.utils.Constants;
import org.bigdiff.utils.PackageInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

public class AppLayoutsController {
    private static final Logger logger = LoggerFactory.getLogger(AppLayoutsController.class);
    private File[] apkDirs;
    AtomicInteger sequenceId;

    public AppLayoutsController(File[] apkDirs) {
        this.apkDirs = apkDirs;
        this.sequenceId = new AtomicInteger();
    }

    public void createGraphML() {
        int count = 0;
        for (File apkDir : apkDirs) {
            HashMap<String, String> appInfo = getAppInfo(apkDir);
            if (appInfo != null && !Strings.isNullOrEmpty(appInfo.get("package")) &&
                    !Strings.isNullOrEmpty(appInfo.get("versionCode")) &&
                    !Strings.isNullOrEmpty(appInfo.get("versionName"))) {
                String packageName = appInfo.get("package");
                String versionCode = appInfo.get("versionCode");
                String versionName = appInfo.get("versionName");
                logger.info("{} - Parsing package {}, version code:{}", count, packageName, versionCode);
                String graphMLFileName = packageName + "-" + versionCode + ".graphml";
                File graphmlFile = new File(apkDir, Constants.UI_GRAPHML_DIR + File.separator +
                        graphMLFileName);
                if (graphmlFile.exists()){
                    if(!graphmlFile.delete()){
                        logger.error("Failed to delete existing graphml file {}",
                                graphmlFile.getAbsoluteFile());
                        continue;
                    }
                }
                try {
                    FileUtils.forceMkdir(graphmlFile.getParentFile());
                } catch (IOException e) {
                    logger.error("Failed to create output directory {}",
                            graphmlFile.getParentFile().getAbsoluteFile(), e);
                    continue;
                }
                GraphMLWriter graphMLWriter = new GraphMLWriter(
                        graphmlFile.getAbsolutePath());
                // App node
                String appNodeId = Integer.toString(sequenceId.incrementAndGet());
                createAppNode(graphMLWriter, packageName, versionCode, versionName,
                        appNodeId);

                // List all layout directories
                File[] layoutDirs = getLayoutDirs(apkDir);
                // create directory and file nodes
                for (File layoutDir : layoutDirs) {
                    Collection<File> layoutFiles = getLayoutFiles(layoutDir);
                    if (layoutFiles != null) {
                        // Create directory node
                        String dirNodeId = Integer.toString(sequenceId.incrementAndGet());
                        String edgeNodeId = Integer.toString(sequenceId.incrementAndGet());
                        createDirNode(graphMLWriter, layoutDir.getName(), appNodeId,
                                dirNodeId, edgeNodeId);
                        for (File layoutFile : layoutFiles) {
                            // Create File node
                            String fileNodeId = Integer.toString(sequenceId.incrementAndGet());
                            edgeNodeId = Integer.toString(sequenceId.incrementAndGet());
                            createFileNode(graphMLWriter, layoutFile.getName(), dirNodeId, fileNodeId, edgeNodeId);
                            // Parse Layout file
                            LayoutParser layoutParser = new LayoutParser(layoutFile, graphMLWriter, sequenceId, fileNodeId);
                            layoutParser.parse();
                        }
                    } else {
                        logger.info("No layout files found in {} ", apkDir.getAbsolutePath());
                    }
                }
                if (graphMLWriter != null) {
                    graphMLWriter.closeWrite();
                }
                logger.info("GraphML has been written at {}",
                        graphmlFile.getAbsolutePath());

            } else {
                logger.error("Unable to find package name and version values for {}",
                        apkDir.getAbsolutePath());
            }
            count++;
        }

    }

    /**
     * Returns layout directories
     *
     * @param apkDir the root unpacked apk directory
     * @return an array of layout directories
     */
    private File[] getLayoutDirs(File apkDir) {
        File resDir = new File(apkDir, "res");
        File[] layoutDirs = null;
        if (resDir.exists() && resDir.isDirectory()) {
            layoutDirs = resDir.listFiles(new FilenameFilter() {
                @Override
                public boolean accept(File current, String name) {
                    if (name.startsWith("layout")) {
                        return new File(current, name).isDirectory();
                    }
                    return false;
                }
            });
        }
        return layoutDirs;
    }

    /**
     * Returns all layout files in the given layout directory
     *
     * @param layoutDir the layout directory
     * @return a collection of the layout files in the given layout directory
     */
    private Collection<File> getLayoutFiles(File layoutDir) {
        Collection<File> layoutFiles = FileUtils.listFiles(layoutDir,
                new String[]{"xml", "XML"}, false);
        if (layoutFiles != null && layoutFiles.size() > 0) {
            return layoutFiles;
        } else {
            logger.info("No layout file found in {}",
                    layoutDir.getAbsolutePath());
        }
        return null;
    }

    private void createAppNode(GraphMLWriter graphMLWriter, String packageName, String versionCode,
                               String versionName, String appNodeId) {
        Map<Object, Object> mapApp = new HashMap<Object, Object>();
        mapApp.put("name", packageName);
        mapApp.put("version_code", versionCode);
        mapApp.put("version_name", versionName);
        mapApp.put("labels", "App");
        graphMLWriter.writeNode(appNodeId, mapApp);
    }

    // Create Resource Directory Node
    private void createDirNode(GraphMLWriter graphMLWriter, String directoryName,
                               String parenNodeId, String dirNodeId, String edgeId) {
        Map<Object, Object> mapDir = new HashMap<Object, Object>();
        mapDir.put("directory_name", directoryName);
        mapDir.put("labels", "Directory");
        graphMLWriter.writeNode(dirNodeId, mapDir);
        graphMLWriter.writeEdge(edgeId, parenNodeId, dirNodeId, "HAS_DIR",
                null);
    }

    // Create Layout File  Node
    private void createFileNode(GraphMLWriter graphMLWriter, String fileName,
                                String parenNodeId, String fileNodeId, String edgeId) {
        Map<Object, Object> mapFile = new HashMap<Object, Object>();
        mapFile.put("file", fileName);
        mapFile.put("labels", "File");
        graphMLWriter.writeNode(fileNodeId, mapFile);
        graphMLWriter
                .writeEdge(edgeId, parenNodeId, fileNodeId, "HAS_FILE", null);
    }

    private HashMap<String, String> getAppInfo(File apkDir) {
        HashMap<String, String> appInfo = null;
        String packageName = PackageInfo.getPackageNameFromManifest(new File(apkDir, "AndroidManifest.xml"));
        HashMap<String, String> appVersion = PackageInfo.getVersionFromYAMLFile(new File(apkDir, "apktool.yml"));
        if (appVersion == null) {
            appVersion = PackageInfo.getVersionFromManifest(new File(apkDir, "AndroidManifest.xml"));
            if (appVersion != null) {
                appInfo = new HashMap<String, String>();
                appInfo.put("package", packageName);
                appInfo.put("versionCode", appVersion.get("versionCode"));
                appInfo.put("versionName", appVersion.get("versionName"));
            }
        } else {
            appInfo = new HashMap<String, String>();
            appInfo.put("package", packageName);
            appInfo.put("versionCode", appVersion.get("versionCode"));
            appInfo.put("versionName", appVersion.get("versionName"));
        }
        return appInfo;
    }


}
