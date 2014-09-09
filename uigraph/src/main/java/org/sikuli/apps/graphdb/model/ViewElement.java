package org.sikuli.apps.graphdb.model;

import java.util.List;

import org.neo4j.graphdb.Node;

public class ViewElement {
	private String name;
	private Node node;

	public ViewElement(Node node, String name) {
		this.node = node;
		this.name = name;
		this.node.setProperty("name", name);
	}

	public Node getNode() {
		return node;
	}

	public void setNode(Node node) {
		this.node = node;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public void setProperties(List<ViewProperty> properties) {
		for (ViewProperty propery : properties) {
			this.node.setProperty(propery.getName(), propery.getValue());
		}
	}

	public ViewProperty getProperty(String name) {
		return (ViewProperty) node.getProperty(name);
	}

}
