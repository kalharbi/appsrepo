package org.sikuli.apps.graphdb.model;

import org.neo4j.graphdb.RelationshipType;

public enum RelationshipTypes implements RelationshipType {
	HAS_VERSION, // Connects an app with its version.
	HAS_DIR, // Connects an app version with its layout directory.
	HAS_FILE, // Connects an app directory with its layout files.
	HAS_VIEW_GROUP, // Connects a layout file with its view groups, or a view
					// group with another view group.
	HAS_VIEW // Connects a view group with its views.
}
