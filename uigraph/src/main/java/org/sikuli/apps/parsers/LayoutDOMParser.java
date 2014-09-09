/**
Khalid
 */
package org.sikuli.apps.parsers;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import org.sikuli.apps.graphdb.drivers.UILayoutService;
import org.sikuli.apps.graphdb.model.ViewProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class LayoutDOMParser {
	private final static Logger logger = LoggerFactory
			.getLogger(LayoutDOMParser.class);
	private File layoutXMLFile;
	private UILayoutService service;
	private org.neo4j.graphdb.Node graphParentNode, tmpGraphParentNode;

	public LayoutDOMParser(File layoutXMLFile,
			org.neo4j.graphdb.Node graphParentNode, UILayoutService service) {
		this.layoutXMLFile = layoutXMLFile;
		this.graphParentNode = graphParentNode;
		this.service = service;
	}

	public void parse() {
		try {
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory
					.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(this.layoutXMLFile);
			doc.getDocumentElement().normalize();
			Element rootElement = doc.getDocumentElement();
			// skip merge layout files
			if (rootElement.getTagName().equals("merge")) {
				this.service.forceDeleteNode(this.graphParentNode);
				return;
			}
			// If the relationship is include
			else if (rootElement.getTagName().equals("include")) {
				String layoutFilePath = rootElement.getAttribute("layout")
						.replace("@", "") + ".xml";
				File includedLayoutFile = new File(
						this.layoutXMLFile.getParent(), layoutFilePath);
				if (layoutFilePath != null && includedLayoutFile.exists()) {
					doIncludeLayoutFile(includedLayoutFile,
							this.graphParentNode);
					this.tmpGraphParentNode = null;
				}
			}
			if(this.layoutXMLFile.getName().equals("second_layout.xml")){
				System.out.println("In file");
			}
			if (rootElement.hasChildNodes()) {
				List<ViewProperty> properties = getElementAttributes(
						this.layoutXMLFile, rootElement);
				this.graphParentNode = service.createRootViewGroupElement(
						rootElement.getTagName(), properties,
						this.graphParentNode).getNode();
				visitRecursively(rootElement, this.layoutXMLFile);
			} else {
				List<ViewProperty> properties = getElementAttributes(
						this.layoutXMLFile, rootElement);
				this.graphParentNode = service.createRootViewElement(
						rootElement.getTagName(), properties,
						this.graphParentNode).getNode();
			}
		} catch (Exception e) {
			logger.error("Error: ", e);
		}
	}

	/**
	 * Visits DOM nodes recursively and inserts views and view groups into the
	 * graph database.
	 * 
	 * @param node
	 *            The start DOM node.
	 * @param xmlFile
	 *            The XML file to be parsed.
	 */
	private void visitRecursively(Element node, File xmlFile) {
		// get all child nodes
		NodeList list = node.getChildNodes();
		for (int i = 0; i < list.getLength(); i++) {
			// get child node
			Node childNode = list.item(i);
			if (childNode.getNodeType() == Node.ELEMENT_NODE) {
				// view group element
				if (childNode.hasChildNodes()) {
					List<ViewProperty> properties = getElementAttributes(
							xmlFile, (Element) childNode);
					this.graphParentNode = this.service.createViewGroupElement(
							childNode.getNodeName(), properties,
							this.graphParentNode).getNode();
				} else {
					// view element or include
					if (childNode.getNodeName().equals("include")) {
						String layoutFilePath = ((Element) childNode)
								.getAttribute("layout").replace("@", "")
								+ ".xml";
						File parent = new File(xmlFile.getParent());
						File includedLayoutFile = new File(parent.getParent(),
								layoutFilePath);
						if (layoutFilePath != null
								&& includedLayoutFile.exists()) {
							doIncludeLayoutFile(includedLayoutFile,
									this.graphParentNode);
						}
					} else {
						List<ViewProperty> properties = getElementAttributes(
								xmlFile, (Element) childNode);
						this.service.createViewElement(childNode.getNodeName(),
								properties, this.graphParentNode).getNode();
					}

				}
			}
			//visitRecursively((Element)childNode, xmlFile);
		}
	}

	private List<ViewProperty> getElementAttributes(File xmlFile,
			Element element) {
		List<ViewProperty> properties = new ArrayList<ViewProperty>();
		NamedNodeMap namedNodeMap = element.getAttributes();
		for (int i = 0; i < namedNodeMap.getLength(); i++) {
			Attr attr = (Attr) namedNodeMap.item(i);
			String key = attr.getNodeName();
			String value = attr.getNodeValue();
			File valuesDir = new File(xmlFile.getParentFile().getParentFile(),
					"values");
			if (value.startsWith("@color")) {
				File colorsFile = new File(valuesDir, "colors.xml");
				if (colorsFile.exists()) {
					value = getResourceValue(colorsFile, "color",
							value.replace("@color/", ""));
				}
			} else if (value.startsWith("@string")) {
				File stringsFile = new File(valuesDir, "strings.xml");
				if (stringsFile.exists()) {
					value = getResourceValue(stringsFile, "string",
							value.replace("@string/", ""));
				}
			} else if (value.startsWith("@dimen")) {
				File dimensFile = new File(valuesDir, "dimens.xml");
				if (dimensFile.exists()) {
					value = getResourceValue(dimensFile, "dimen",
							value.replace("@dimen/", ""));
				}
			} /*
			 * TODO else if (value.startsWith("@style")) { File stylesFile = new
			 * File(valuesDir, "styles.xml"); if (stylesFile.exists()) {
			 * HashMap<String, String> attrsMap =
			 * getResourceMapValues(stylesFile, "style",
			 * value.replace("@style/", "")); for (Map.Entry<String, String>
			 * entry : attrsMap.entrySet()){ System.out.println(entry.getKey() +
			 * "/" + entry.getValue()); } } }
			 */
			properties.add(new ViewProperty(key, value));
		}
		return properties;

	}

	private void doIncludeLayoutFile(File includedLayoutFile,
			org.neo4j.graphdb.Node parent) {
		try {
			DocumentBuilderFactory dbFactory = DocumentBuilderFactory
					.newInstance();
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(includedLayoutFile);
			this.tmpGraphParentNode = parent;
			Node node = doc.getDocumentElement();
			doParseIncludeElements(node, includedLayoutFile);

		} catch (Exception e) {
			logger.error("Error: ", e);
		}
	}

	private void doParseIncludeElements(Node node, File xmlFile) {
		// get all child nodes
		NodeList list = node.getChildNodes();
		for (int i = 0; i < list.getLength(); i++) {
			// get child node
			Node childNode = list.item(i);
			if (childNode.getNodeType() == Node.ELEMENT_NODE) {
				// view group element
				if (childNode.hasChildNodes()) {
					if (((Element) childNode).getTagName().equals("merge")) {
						continue;
					}
					List<ViewProperty> properties = getElementAttributes(
							xmlFile, (Element) childNode);
					this.tmpGraphParentNode = this.service
							.createViewGroupElement(childNode.getNodeName(),
									properties, this.tmpGraphParentNode)
							.getNode();
				} else {
					// view element or include
					if (childNode.getNodeName().equals("include")) {
						String layoutFilePath = ((Element) childNode)
								.getAttribute("layout").replace("@", "")
								+ ".xml";
						File parent = new File(xmlFile.getParent());
						File includedLayoutFile = new File(parent.getParent(),
								layoutFilePath);
						if (layoutFilePath != null
								&& includedLayoutFile.exists()) {
							doIncludeLayoutFile(includedLayoutFile,
									this.tmpGraphParentNode);
						}
					} else {
						List<ViewProperty> properties = getElementAttributes(
								xmlFile, (Element) childNode);
						this.service.createViewElement(childNode.getNodeName(),
								properties, this.tmpGraphParentNode).getNode();
					}

				}
			}
			//	doParseIncludeElements(childNode, xmlFile);
		}
	}

	private String getResourceValue(File resourceFile, String resourceType,
			String resourceIdName) {
		try {
			DocumentBuilderFactory factory = DocumentBuilderFactory
					.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();
			Document doc = builder.parse(resourceFile);
			XPathFactory xPathfactory = XPathFactory.newInstance();
			XPath xpath = xPathfactory.newXPath();
			String expression = "//" + resourceType + "[@name=\""
					+ resourceIdName + "\"]";
			XPathExpression xpathExpr = xpath.compile(expression);
			NodeList nodeList = (NodeList) xpathExpr.evaluate(doc,
					XPathConstants.NODESET);
			if (nodeList != null) {
				String value = "";
				for (int i = 0; i < nodeList.getLength(); i++) {
					value += nodeList.item(i).getTextContent();
					if (nodeList.getLength() > 1) {
						value += " ";
					}
				}
				return value;
			}
		} catch (XPathExpressionException e) {
			logger.error("Error: ", e);
		} catch (SAXException e) {
			logger.error("Error: ", e);
		} catch (IOException e) {
			logger.error("Error: ", e);
		} catch (ParserConfigurationException e) {
			logger.error("Error: ", e);
		}
		return null;
	}
}
