/**
Khalid
 */
package org.sikuli.apps.graphdb.model;

import java.util.List;

import org.neo4j.graphdb.Node;

public class ViewGroupElement {

	private String name;
	private Node node;

	public ViewGroupElement(Node node, String name) {
		this.node = node;
		this.name = name;
		this.node.setProperty("name", name);
	}

	public String getName() {
		return this.name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Node getNode() {
		return node;
	}

	public void setNode(Node node) {
		this.node = node;
	}

	/*public void addSubViewGroupElement(ViewGroupElement viewGroup) {
		Node viewGroupNode = viewGroup.getNode();
		this.node.createRelationshipTo(viewGroupNode,
				RelationshipTypes.HAS_VIEW_GROUP);
	}

	public void addView(ViewElement view) {
		Node viewNode = view.getNode();
		this.node.createRelationshipTo(viewNode, RelationshipTypes.HAS_VIEW);
	}*/

	public void setProperties(List<ViewProperty> properties) {
		for (ViewProperty propery : properties) {
			this.node.setProperty(propery.getName(), propery.getValue());
		}
	}

	public ViewProperty getProperty(String name) {
		return (ViewProperty) node.getProperty(name);
	}

}