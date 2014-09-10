/**
Khalid
 */
package org.sikuli.apps.graphdb.drivers;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.neo4j.cypher.javacompat.ExecutionEngine;
import org.neo4j.cypher.javacompat.ExecutionResult;
import org.neo4j.graphdb.DynamicLabel;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.ResourceIterator;
import org.neo4j.graphdb.Transaction;
import org.neo4j.helpers.collection.IteratorUtil;
import org.sikuli.apps.graphdb.model.RelationshipTypes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UIGraphMatch {
	private static final Logger logger = LoggerFactory
			.getLogger(UIGraphMatch.class);
	private final GraphDatabaseService graphDb;
	private final ExecutionEngine engine;

	public UIGraphMatch(GraphDatabaseService graphDb, ExecutionEngine engine) {
		this.graphDb = graphDb;
		this.engine = engine;
	}

	public ArrayList<Node> findNode(String labelName, String propertyName,
			String propertyValue) {
		ArrayList<Node> appNodes = new ArrayList<Node>();
		Label label = DynamicLabel.label(labelName);
		try (Transaction tx = graphDb.beginTx()) {
			try (ResourceIterator<Node> apps = graphDb
					.findNodesByLabelAndProperty(label, propertyName,
							propertyValue).iterator()) {
				while (apps.hasNext()) {
					appNodes.add(apps.next());
				}
			}
		}
		return appNodes;
	}

	/**
	 * Returns a list of nodes that match the cypher query: <br/>
	 * MATCH (app: label1Name {property1Name :'property1Value'})-[
	 * relation.name()]->(n2:label2Name {property2Name : 'property2Value'})
	 * RETURN app,n2 <br/>
	 * Cypher query Example: <br/>
	 * MATCH
	 * (app:App{name:'com.evernote'})-[HAS_VERSION]-(verc:Version{verc:1234})
	 * RETURN app,verc
	 * 
	 * @param label1Name
	 *            the first label name
	 * @param property1Name
	 *            the property name of the first label
	 * @param property1Value
	 *            the property value of the first label
	 * @param relation
	 *            the relationship type between the two labels
	 * @param label2Name
	 *            the second label name
	 * @param property2Name
	 *            the property name of the second label
	 * @param property2Value
	 *            the property value of the second label
	 * @return a list of type {@link ArrayList}<{@link Node}> nodes that match
	 *         the cypher query.
	 */
	public ArrayList<Node> matchesTwoNodes(String label1Name,
			String property1Name, String property1Value,
			RelationshipTypes relation, String label2Name,
			String property2Name, String property2Value) {
		ArrayList<Node> matchedNodes = new ArrayList<Node>();
		try (Transaction tx = graphDb.beginTx()) {
		String query = "MATCH (app:" + label1Name + "{" + property1Name + ":'"
				+ property1Value + "'})-[" + relation.name() + "]->(n2:"
				+ label2Name + "{" + property2Name + ":" + property2Value
				+ "}) RETURN app,n2";
		ExecutionResult result = engine.execute(query);
		List<String> columns = result.columns();
		if (columns != null && columns.size() > 0) {
			Iterator<Node> n_column = result.columnAs("app");
			for (Node node : IteratorUtil.asIterable(n_column)) {
				matchedNodes.add(node);
			}

		}
		tx.success();
		}
		return matchedNodes;
	}
}
