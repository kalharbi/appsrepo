package org.bigdiff.graph;


import org.neo4j.cypher.javacompat.ExecutionEngine;
import org.neo4j.graphdb.*;
import org.neo4j.graphdb.schema.IndexDefinition;
import org.neo4j.graphdb.schema.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;

/**
 * @author Khalid Alharbi
 */
public class DataStoreTransaction {
    private static final Logger logger = LoggerFactory.getLogger(DataStoreTransaction.class);
    private final GraphDatabaseService graphDb;
    private final ExecutionEngine engine;

    public DataStoreTransaction(GraphDatabaseService graphDb, ExecutionEngine engine) {
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
     * Create index on the given label and property.
     *
     * @param label    the Label to create index for.
     * @param property the property to index on.
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
     * @param label the Label to get indexes for.
     * @return all indexes attached to the given label, or null if there were
     * none matching the label.
     */
    private Iterable<IndexDefinition> getIndexByLabel(Label label) {
        Iterable<IndexDefinition> x = null;
        try (Transaction tx = graphDb.beginTx()) {
            x = graphDb.schema().getIndexes(label);
            tx.success();
        }
        return x;
    }

    /**
     * @param label    the indexed label.
     * @param property the indexed property.
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

}
