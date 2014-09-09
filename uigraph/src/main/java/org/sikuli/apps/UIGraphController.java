/**
Khalid
 */
package org.sikuli.apps;

import java.io.File;
import java.io.FilenameFilter;
import java.util.ArrayList;
import java.util.Collection;

import org.apache.commons.io.FileUtils;
import org.neo4j.graphdb.Node;
import org.sikuli.apps.graphdb.drivers.UIGraphMatch;
import org.sikuli.apps.graphdb.drivers.UILayoutService;
import org.sikuli.apps.graphdb.model.RelationshipTypes;
import org.sikuli.apps.parsers.LayoutDOMParser;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UIGraphController {
	private final static Logger logger = LoggerFactory
			.getLogger(UIGraphController.class);
	UILayoutService service;
	UIGraphMatch uiGraphMatch;

	public void startUIGraph(File apkDir, String packageName,
			String versionCode, String versionName) {
		// Insert the app root node
		ArrayList<Node> appNodes = uiGraphMatch.findNode("App", "name",
				packageName);
		Node appNode;
		if (appNodes != null && appNodes.size() > 0) {
			appNode = appNodes.get(0);
			logger.info("App {} already exists.", packageName);
		} else {
			appNode = service.createAppNode(packageName);
		}
		
		ArrayList<Node> versionsNode = uiGraphMatch.matchesTwoNodes("App",
				"name", packageName, RelationshipTypes.HAS_VERSION, "Version",
				"verc", versionCode);

		if (versionsNode.size() > 0) {
			logger.info("Package {}, version: {}, already exists.",
					packageName, versionCode);
			return;
		}

		Node versionNode = service.createVersionNode(
				Long.parseLong(versionCode), versionName, appNode);
		// List all layout directories
		File resDir = new File(apkDir, "res");
		if (resDir.exists() && resDir.isDirectory()) {
			File[] layoutDirs = resDir.listFiles(new FilenameFilter() {
				@Override
				public boolean accept(File current, String name) {
					if (name.startsWith("layout")) {
						return new File(current, name).isDirectory();
					}
					return false;
				}
			});
			if (layoutDirs != null && layoutDirs.length > 0) {
				for (File layoutDir : layoutDirs) {
					Node layoutDirNode = insertLayoutDirNode(layoutDir,
							versionNode);
					// get all layout files inside this layout directory.
					Collection<File> layoutFiles = FileUtils.listFiles(
							layoutDir, new String[] { "xml", "XML" }, false);
					insertLayoutFileNode(layoutFiles, layoutDirNode);
				}
			} else {
				logger.info("Np layout directory found in {}",
						apkDir.getAbsolutePath());
			}
		} else {
			logger.info("No res/ directory in {} ", apkDir.getAbsolutePath());
		}

	}

	private Node insertLayoutDirNode(File layoutDir, Node parent) {
		// Insert the directory to the app version name
		return service.createLayoutDirectory(layoutDir.getName(), parent);
	}

	private void insertLayoutFileNode(Collection<File> layoutFiles, Node parent) {
		// Insert the directory to the app version name
		for (File layoutFile : layoutFiles) {
			Node layoutFileNode = service.createLayoutFile(
					layoutFile.getName(), parent);
			new LayoutDOMParser(layoutFile, layoutFileNode, service).parse();
		}
	}

	public void setup() {
		service = new UILayoutService();
		uiGraphMatch = new UIGraphMatch(service.getGraphDatabase(),
				service.getExecutionEngine());
		// Create App.name index if it does not exist
		if (!service.isIndexed("App", "name")) {
			service.createIndexFor("App", "name");
		}
	}

	public void shutdown() {
		service.shutdown();
	}

}
