/**
Khalid
 */
package org.bigdiff.graphmlwriters;

import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GraphMLWriter {

	private final static Logger logger = LoggerFactory
			.getLogger(GraphMLWriter.class);
	private String fileName;
	private Writer writer = null;
	private String graphMLHeader = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
			+ System.lineSeparator()
			+ "<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\">"
			+ System.lineSeparator()
			+ "<graph id=\"G\" edgedefault=\"directed\">";
	private String graphMLFooter = "</graph>" + System.lineSeparator()
			+ "</graphml>";

	public GraphMLWriter(String fileName) {
		this.fileName = fileName;
		String encoding = "utf-8";
		try {
			writer = new BufferedWriter(new OutputStreamWriter(
					new FileOutputStream(this.fileName, false), encoding));
			writer.write(this.graphMLHeader + System.lineSeparator());
		} catch (UnsupportedEncodingException e) {
			logger.error("encoding {} is not supported, {}", encoding, e);
		} catch (FileNotFoundException e) {
			logger.error("File Not found {}, {}", fileName, e);
		} catch (IOException e) {
			logger.error("IO Exception while writing to file: {}, {}",
					fileName, e);
		}
	}

	/**
	 * Write a graph node (vertex) using the GraphML representation.
	 * 
	 * @param nodeId
	 *            node id of the node in the beginning of the vertex
	 *            representation.
	 * @param dataMap
	 *            a map of key/value pairs associated with the given graph
	 *            nodeId element.
	 */
	public void writeNode(String nodeId, Map<Object, Object> dataMap) {
		try {
			writer.write("<node id=\"" + nodeId + "\">"
					+ System.lineSeparator());
			if (dataMap != null) {
				for (Map.Entry<Object, Object> entry : dataMap.entrySet()) {
					Object key = entry.getKey();
					Object value = entry.getValue();
					writer.write("<data key=\"" + key + "\">" + value
							+ "</data>" + System.lineSeparator());
				}
			}
			writer.write("</node>" + System.lineSeparator());
		} catch (IOException e) {
			logger.error("IO Exception while writing to file: {}, {}",
					fileName, e);
		}
	}

	/**
	 * Writes the graph edge that connects the source and target nodes together.
	 * 
	 * @param edgeId
	 *            the edge Id
	 * @param sourceId
	 *            the identifier of the source node.
	 * @param targetId
	 *            the identifier of the target node.
	 * @param label
	 *            a label denoting the relationship represented by the edge.
	 * @param dataMap
	 *            a map of edge properties defined by a map from key to value.
	 */
	public void writeEdge(String edgeId, String sourceId, String targetId,
			String label, Map<Object, Object> dataMap) {
		try {
			writer.write("<edge id=\"" + edgeId + "\" source=\"" + sourceId
					+ "\" target=\"" + targetId + "\" label=\"" + label + "\">"
					+ System.lineSeparator());
			if (dataMap != null) {
				for (Map.Entry<Object, Object> entry : dataMap.entrySet()) {
					Object key = entry.getKey();
					Object value = entry.getValue();
					writer.write("<data key=\"" + key + "\">" + value
							+ "</data>" + System.lineSeparator());
				}
			}
			writer.write("</edge>" + System.lineSeparator());

		} catch (IOException e) {
			logger.error("IO Exception while writing to file: {}, {}",
					fileName, e);
		}
	}

	public void closeWrite() {
		try {
			writer.write(graphMLFooter + System.lineSeparator());
			writer.close();
		} catch (IOException e) {
			logger.error(
					"Failed to writer or close the writing stream of: {}, {}",
					fileName, e);
		}
	}

}
