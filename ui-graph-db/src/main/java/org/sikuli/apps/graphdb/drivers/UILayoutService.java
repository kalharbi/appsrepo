/**
Khalid
 */
package org.sikuli.apps.graphdb.drivers;

import java.util.List;

import org.neo4j.cypher.javacompat.ExecutionEngine;
import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.DynamicLabel;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.neo4j.graphdb.schema.IndexDefinition;
import org.neo4j.graphdb.schema.Schema;
import org.sikuli.apps.graphdb.model.RelationshipTypes;
import org.sikuli.apps.graphdb.model.ViewElement;
import org.sikuli.apps.graphdb.model.ViewGroupElement;
import org.sikuli.apps.graphdb.model.ViewProperty;
import org.sikuli.apps.utils.Constants;

public class UILayoutService {

	//private static final String DB_PATH = "/Users/khalid/neo4j-data/appsgraph/";
	//private static final String NEO_HOME = "/Users/Khalid/dev/neo4j/neo4j-community-2.1.3/";

	private final GraphDatabaseService graphDb;
	private final ExecutionEngine engine;

	public UILayoutService() {
		this.graphDb = new GraphDatabaseFactory()
				.newEmbeddedDatabaseBuilder(Constants.DB_PATH)
				.loadPropertiesFromFile(Constants.NEO_HOME + "conf/neo4j.properties")
				.newGraphDatabase();
		registerShutdownHook(this.graphDb);
		this.engine = new ExecutionEngine(graphDb);
	}

	public GraphDatabaseService getGraphDatabase() {
		return this.graphDb;
	}

	public ExecutionEngine getExecutionEngine() {
		return this.engine;
	}

	/**
	 * Create index on the given label and property.
	 * 
	 * @param label
	 *            the Label to create index for.
	 * @param property
	 *            the property to index on.
	 */
	public void createIndexFor(String label, String property) {
		try (Transaction tx = graphDb.beginTx()) {
			Schema schema = graphDb.schema();
			schema.indexFor(DynamicLabel.label(label)).on(property).create();
			tx.success();
		}
	}

	/**
	 * Get indexes by Label.
	 * 
	 * @param label
	 *            the Label to get indexes for.
	 * @return all indexes attached to the given label, or null if there were
	 *         none matching the label.
	 */
	public Iterable<IndexDefinition> getIndexByLabel(Label label) {

		Iterable<IndexDefinition> x = null;
		try (Transaction tx = graphDb.beginTx()) {
			x = graphDb.schema().getIndexes(label);
			tx.success();
		}
		return x;
	}

	/**
	 * 
	 * @param label
	 *            the indexed label.
	 * @param property
	 *            the indexed property.
	 * @return True if the index exists; otherwise False.
	 */
	public boolean isIndexed(String label, String property) {
		try (Transaction tx = graphDb.beginTx()) {
			Iterable<IndexDefinition> indexes = getIndexByLabel(DynamicLabel
					.label(label));
			for (IndexDefinition index : indexes) {
				for (String key : index.getPropertyKeys()) {
					if (key.equals(property)) {
						return true;
					}
				}
			}
			tx.success();
		}
		return false;
	}

	public void shutdown() {
		this.graphDb.shutdown();
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

	/**
	 * Insert a new root app node.
	 * 
	 * @param name
	 *            The value of the name property of the node to be inserted.
	 * @return {@link Node} object for the new inserted node.
	 */
	public Node createAppNode(String packageName) {
		try (Transaction tx = graphDb.beginTx()) {
			Label label = DynamicLabel.label("App");
			Node appNode = graphDb.createNode(label);
			appNode.setProperty("name", packageName);
			tx.success();
			return appNode;
		}
	}

	/**
	 * Insert a new version node.
	 * 
	 * @param VersionCode
	 *            The version code of the new app.
	 * @param VersionName
	 *            The version name of the app.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link Node} object node for the new inserted version node.
	 */
	public Node createVersionNode(long VersionCode, String VersionName,
			Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			Label label = DynamicLabel.label("Version");
			Node versionNode = graphDb.createNode(label);
			versionNode.setProperty("vern", VersionName);
			versionNode.setProperty("verc", VersionCode);
			parent.createRelationshipTo(versionNode,
					RelationshipTypes.HAS_VERSION);
			tx.success();
			return versionNode;
		}
	}

	/**
	 * Insert a new view group node node.
	 * 
	 * @param name
	 *            The value of the name property of the node to be inserted.
	 * @param properties
	 *            The properties of the node to be inserted.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link ViewGroupElement} object node for the new inserted node.
	 */
	public ViewGroupElement createViewGroupElement(final String name,
			final List<ViewProperty> properties, final Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			Label label = DynamicLabel.label("ViewGroup");
			Node viewGroupNode = graphDb.createNode(label);
			final ViewGroupElement viewGroupElement = new ViewGroupElement(
					viewGroupNode, name);
			viewGroupElement.setProperties(properties);
			parent.createRelationshipTo(viewGroupElement.getNode(),
					RelationshipTypes.HAS_VIEW_GROUP);
			tx.success();
			return viewGroupElement;
		}
	}

	/**
	 * Insert a new view group node as a root node for the file graph node.
	 * 
	 * @param name
	 *            The value of the name property of the node to be inserted.
	 * @param properties
	 *            The properties of the node to be inserted.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link ViewGroupElement} object node for the new inserted node.
	 */
	public ViewGroupElement createRootViewGroupElement(final String name,
			final List<ViewProperty> properties, final Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			if (!parent.hasRelationship(RelationshipTypes.HAS_FILE,
					Direction.INCOMING)) {
				throw new IllegalArgumentException(
						"A root view group can only be added to a "
								+ "layout file node.");
			}

			Label label1 = DynamicLabel.label("ViewGroup");
			//Label label2 = DynamicLabel.label("root");
			Node viewGroupNode = graphDb.createNode(label1);
			final ViewGroupElement viewGroupElement = new ViewGroupElement(
					viewGroupNode, name);
			viewGroupElement.setProperties(properties);
			parent.createRelationshipTo(viewGroupElement.getNode(),
					RelationshipTypes.HAS_VIEW_GROUP);
			tx.success();
			return viewGroupElement;
		}
	}

	/**
	 * Insert a new view node as a root node for the file graph node.
	 * 
	 * @param name
	 *            The value of the name property of the node to be inserted.
	 * @param properties
	 *            The properties of the node to be inserted.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link ViewElement} object node for the new inserted node.
	 */
	public ViewElement createRootViewElement(final String name,
			final List<ViewProperty> properties, final Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			if (!parent.hasRelationship(RelationshipTypes.HAS_FILE,
					Direction.INCOMING)) {
				throw new IllegalArgumentException(
						"A root view can only be added to a "
								+ "layout file node.");
			}
			Label label1 = DynamicLabel.label("View");
			//Label label2 = DynamicLabel.label("root");
			Node viewNode = graphDb.createNode(label1);
			final ViewElement viewElement = new ViewElement(viewNode, name);
			viewElement.setProperties(properties);
			parent.createRelationshipTo(viewElement.getNode(),
					RelationshipTypes.HAS_VIEW_GROUP);
			tx.success();
			return viewElement;
		}
	}

	/**
	 * Insert a new view node.
	 * 
	 * @param name
	 *            The value of the name property of the node to be inserted.
	 * @param properties
	 *            The properties of the node to be inserted.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link ViewElement} object node for the new inserted node.
	 */
	public ViewElement createViewElement(final String name,
			final List<ViewProperty> properties, final Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			if (!parent.hasRelationship(RelationshipTypes.HAS_VIEW_GROUP,
					Direction.INCOMING)) {
				throw new IllegalArgumentException(
						"A view can only be added to a "
								+ "parent view group node.");
			}
			Label label = DynamicLabel.label("View");
			Node viewNode = graphDb.createNode(label);
			final ViewElement viewElement = new ViewElement(viewNode, name);
			viewElement.setProperties(properties);
			parent.createRelationshipTo(viewElement.getNode(),
					RelationshipTypes.HAS_VIEW);
			tx.success();
			return viewElement;
		}
	}

	/**
	 * Insert a new layout directory node.
	 * 
	 * @param dirName
	 *            The directory name of the new layout directory node.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link Node} object node for the new inserted layout directory
	 *         node.
	 */
	public Node createLayoutDirectory(String dirName, Node parent) {
		try (Transaction tx = graphDb.beginTx()) {

			if (!parent.hasRelationship(RelationshipTypes.HAS_VERSION,
					Direction.INCOMING)) {
				throw new IllegalArgumentException(
						"A directory can only be added to a "
								+ "parent app version node.");
			}
			Label label = DynamicLabel.label("Dir");
			Node dirNode = graphDb.createNode(label);
			dirNode.setProperty("dir", dirName);
			parent.createRelationshipTo(dirNode, RelationshipTypes.HAS_DIR);
			tx.success();
			return dirNode;
		}
	}

	/**
	 * Insert a new layout file node.
	 * 
	 * @param fileName
	 *            The layout file name.
	 * @param parent
	 *            The parent node of the new node to be inserted.
	 * @return {@link Node} object node for the new inserted layout file node.
	 */
	public Node createLayoutFile(String fileName, Node parent) {
		try (Transaction tx = graphDb.beginTx()) {
			if (!parent.hasRelationship(RelationshipTypes.HAS_DIR,
					Direction.INCOMING)) {
				throw new IllegalArgumentException(
						"A file can only be added to a "
								+ "parent directory node.");
			}
			Label label = DynamicLabel.label("File");
			Node fileNode = graphDb.createNode(label);
			fileNode.setProperty("file", fileName);
			parent.createRelationshipTo(fileNode, RelationshipTypes.HAS_FILE);
			tx.success();
			return fileNode;
		}
	}

	/**
	 * Delete a Node.
	 * 
	 * @param labelName
	 *            The label name of the node to be deleted
	 * @param propertyName
	 *            The name of the property.
	 * @param propertyValue
	 *            The value of the property.
	 */
	public void deleteNode(String labelName, String propertyName,
			Object propertyValue) {
		try (Transaction tx = graphDb.beginTx()) {
			Label label = DynamicLabel.label(labelName);

			for (Node node : graphDb.findNodesByLabelAndProperty(label,
					propertyName, propertyValue)) {
				node.delete();
			}
			tx.success();
		}
	}

	/**
	 * Deletes node even if it has relationships
	 * 
	 * @param node
	 */
	public void forceDeleteNode(Node node) {
		try (Transaction tx = graphDb.beginTx()) {
			for (Relationship relation : node.getRelationships()) {
				relation.delete();
			}
			node.delete();
			tx.success();
		}
	}
}
