/**
 Khalid
 */
package org.bigdiff.parsers;

import com.google.common.base.Strings;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringEscapeUtils;
import org.bigdiff.graphmlwriters.GraphMLWriter;
import org.bigdiff.utils.Constants;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.*;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.*;
import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

public class LayoutParser {
    private static final Logger logger = LoggerFactory
            .getLogger(LayoutParser.class);

    // temporarily id to keep track of the parent of layout elements.
    private final String tmpId = "graphml:node-id";
    private File layoutFile;
    private GraphMLWriter graphMLWriter;
    private AtomicInteger sequenceId;
    private String parentNodeId;

    public LayoutParser(File layoutFile, GraphMLWriter graphMLWriter,
                        AtomicInteger sequenceId, String parentNodeId) {
        this.layoutFile = layoutFile;
        this.graphMLWriter = graphMLWriter;
        this.sequenceId = sequenceId;
        this.parentNodeId = parentNodeId;
    }

    private void createNode(String nodeId, String label, String name,
                            Map<Object, Object> attributes) {
        attributes.put("name", name);
        attributes.put("labels", label);
        this.graphMLWriter.writeNode(nodeId, attributes);
    }

    private void createEdge(String label, String sourceId, String targetId,
                            Map<Object, Object> attributes) {
        String edgeId = Integer.toString(this.sequenceId.incrementAndGet());
        graphMLWriter.writeEdge(edgeId, sourceId, targetId, label, attributes);
    }

    public void parse() {
        try {
            final DocumentBuilderFactory dbFactory = DocumentBuilderFactory
                    .newInstance();
            final DocumentBuilder docBuilder = dbFactory.newDocumentBuilder();
            final Document doc = docBuilder.parse(this.layoutFile);

            /* Parse the layout root element
            The root element can be either a ViewGroup, a View, or a <merge> element.
             */
            Element rootElement = doc.getDocumentElement();
            // skip files that start with the
            if (rootElement.getTagName().equals("merge")) {
                return;
            } else {
                String nodeId = Integer.toString(this.sequenceId.incrementAndGet());
                rootElement.setAttribute(tmpId, nodeId);
                String name = rootElement.getTagName();
                Map<Object, Object> attributes = getElementAttributes(rootElement);
                createNode(nodeId, Constants.ROOT,
                        name, attributes);
                createEdge(Constants.HAS_ROOT, this.parentNodeId, nodeId,
                        attributes);
                // parse the rest of layout elements recursively
                parseChildren(rootElement);
            }
        } catch (ParserConfigurationException e) {
            logger.error(
                    "Parser configuration error while parsing xml file: {}",
                    this.layoutFile.getAbsolutePath(), e);

        } catch (IOException e) {
            logger.error("IO exception occurred while parsing xml file: {}",
                    this.layoutFile.getAbsolutePath(), e);

        } catch (SAXException e) {
            logger.error("SAX exception occurred while parsing xml file: {}",
                    this.layoutFile.getAbsolutePath(), e);
        }

    }

    /**
     * Recursively parses layout elements and writes to the GraphML file
     *
     * @param element the element from which the parsing starts.
     */
    private void parseChildren(final Element element) {
        if (element == null) {
            return;
        }
        final NodeList children = element.getChildNodes();
        for (int i = 0; i < children.getLength(); i++) {
            final Node n = children.item(i);
            if (n.getNodeType() == Node.ELEMENT_NODE) {
                String name = n.getNodeName();
                String parentId = ((Element) (n.getParentNode()))
                        .getAttribute(tmpId);
                if (name.equals("include")) {
                    String layoutFilePath = ((Element) n).getAttribute("layout")
                            .replace("@", "") + ".xml";
                    File includedLayoutFile = new File(
                            this.layoutFile.getParentFile().getParent(), layoutFilePath);
                    Element rootIncludedElement = parseEmbeddedLayout(includedLayoutFile, parentId);
                    parseChildren(rootIncludedElement);
                    continue;
                }
                String currentId = Integer.toString(this.sequenceId.incrementAndGet());
                ((Element) n).setAttribute(tmpId, currentId);

                if (n.hasChildNodes()) {
                    Map<Object, Object> attributes = getElementAttributes((Element) n);
                    createNode(currentId, Constants.VIEW_GROUP, name,
                            attributes);
                    createEdge(Constants.HAS_VIEW_GROUP, parentId, currentId,
                            attributes);
                    parseChildren((Element) n);
                } else {
                    Map<Object, Object> attributes = getElementAttributes((Element) n);
                    createNode(currentId, Constants.VIEW, name,
                            attributes);
                    createEdge(Constants.HAS_VIEW, parentId, currentId,
                            attributes);
                }
            }
        }
    }

    /**
     * Parses embedded layouts and returns the root element in the embedded layout file
     *
     * @param includedLayoutFile the embedded layout file
     * @return the root element in the embedded layout file
     */
    private Element parseEmbeddedLayout(File includedLayoutFile, String parentId) {
        try {
            final DocumentBuilderFactory dbFactory = DocumentBuilderFactory
                    .newInstance();
            final DocumentBuilder docBuilder = dbFactory.newDocumentBuilder();
            final Document includedDocument = docBuilder.parse(includedLayoutFile);

            Element e = includedDocument.getDocumentElement();
            String name = e.getNodeName();
            if (name.equals("merge")) {
                NodeList nodeList = ((Node) e).getChildNodes();
                if (nodeList.getLength() == 0) {
                    return null;
                }
                for (int j = 0; j < nodeList.getLength(); j++) {
                    Node childNode = nodeList.item(j);
                    if (childNode.getNodeType() == Node.ELEMENT_NODE) {
                        e = (Element) childNode;
                        name = e.getNodeName();
                    }
                }

            }
            String currentId = Integer.toString(this.sequenceId.incrementAndGet());
            e.setAttribute(tmpId, currentId);
            if (e.hasChildNodes()) {
                Map<Object, Object> attributes = getElementAttributes(e);
                createNode(currentId, Constants.VIEW_GROUP, name,
                        attributes);
                createEdge(Constants.HAS_VIEW_GROUP, parentId, currentId,
                        attributes);
            } else {
                Map<Object, Object> attributes = getElementAttributes(e);
                createNode(currentId, Constants.VIEW, name,
                        attributes);
                createEdge(Constants.HAS_VIEW, parentId, currentId,
                        attributes);
            }
            return e;


        } catch (ParserConfigurationException e) {
            logger.error(
                    "Parser configuration error while parsing xml file: {}",
                    includedLayoutFile.getAbsolutePath(), e);
        } catch (SAXException e) {
            logger.error("SAX exception occurred while parsing xml file: {}",
                    includedLayoutFile.getAbsolutePath(), e);
        } catch (IOException e) {
            logger.error("IO exception occurred while parsing xml file: {}",
                    includedLayoutFile.getAbsolutePath(), e);
        }
        return null;
    }

    /**
     * Returns a map of key/value pairs of the given element's attributes.
     *
     * @param element The element to which the attributes will be retrieved
     * @return a map of the element's attribute.
     */
    private Map<Object, Object> getElementAttributes(Element element) {
        Map<Object, Object> attributes = new HashMap<Object, Object>();
        NamedNodeMap namedNodeMap = element.getAttributes();
        for (int i = 0; i < namedNodeMap.getLength(); i++) {
            Attr attr = (Attr) namedNodeMap.item(i);
            String key = attr.getName();
            if (key.equals(tmpId)) {
                continue;
            }
            String resourceValue = null;
            String value = attr.getNodeValue();
            File valuesDir = new File(this.layoutFile.getParentFile().getParentFile(),
                    "values");
            if (value.startsWith("@") && !value.startsWith("@id") && !value.startsWith("@+id")) {
                try {
                    String resName = value.substring(value.indexOf("@") + 1, value.indexOf("/"));
                    File resFile = new File(valuesDir, resName + "s.xml");
                    if (resFile.exists()) {
                        resourceValue = getResourceValue(resFile, resName,
                                value.replace("@" + resName + "/", ""));
                    }
                    if (Strings.isNullOrEmpty(resourceValue)) {
                        resourceValue = searchAllResourcesValues(valuesDir, resName,
                                value.replace("@" + resName + "/", ""));
                    }
                } catch (IndexOutOfBoundsException e) {
                    logger.error("Failed to find the resource value named: {} referenced in {}", value,
                            this.layoutFile.getAbsolutePath());
                    continue;
                }
            } else {
                resourceValue = value;
            }
            if(resourceValue == null){
                resourceValue = value;
            }
            attributes.put(key, resourceValue);
        }
        return attributes;

    }

    /**
     * Decodes the resource reference into its corresponding value. It returns the String value
     * of the resource after escaping the characters in the value using XML entities.
     *
     * @param resourceFile   The file that contains the reference resource
     * @param resourceType   The resource type (directory name). For example, string for @string
     *                       resources
     * @param resourceIdName The unique identifier name of the resource.
     * @return the corresponding value of the resource reference.
     */
    private String getResourceValue(File resourceFile, String resourceType,
                                    String resourceIdName) {
        String value = null;
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory
                    .newInstance();
            factory.setIgnoringComments(true);
            factory.setIgnoringElementContentWhitespace(true);
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(resourceFile);
            XPathFactory xPathfactory = XPathFactory.newInstance();
            XPath xpath = xPathfactory.newXPath();
            String expression = "//" + resourceType + "[@name=\""
                    + resourceIdName + "\"]";
            XPathExpression xpathExpr = xpath.compile(expression);
            NodeList nodeList = (NodeList) xpathExpr.evaluate(doc,
                    XPathConstants.NODESET);
            if (nodeList != null && nodeList.getLength() > 0) {
                value = "";
                for (int i = 0; i < nodeList.getLength(); i++) {
                    Node n = nodeList.item(i);
                    if (n != null && n.getNodeType() == Node.ELEMENT_NODE) {
                        value += n.getTextContent().trim().replaceAll("\\s+", " ");
                    }
                }
            }
        } catch (XPathExpressionException e) {
            logger.error("XPath Expression Exception while searching {} in {}", resourceIdName, resourceFile.getAbsolutePath(), e);
        } catch (SAXException e) {
            logger.error("SAX Exception while searching for {} in {}", resourceIdName, resourceFile.getAbsolutePath(), e);
        } catch (IOException e) {
            logger.error("IO Exception while searching for {} in {}", resourceIdName, resourceFile.getAbsolutePath(), e);
        } catch (ParserConfigurationException e) {
            logger.error("Parser Configuration Exception while searching for {} in {}", resourceIdName, resourceFile.getAbsolutePath(), e);
        }
        return StringEscapeUtils.escapeXml10(value);
    }

    /**
     * Search all values/*.xml files to find the resource value. It returns the String value
     * of the resource after escaping the characters in the value using XML entities.
     *
     * @param valuesDir      the values/ directory
     * @param resourceType   The resource type (element name). For example, string for @string
     *                       resources
     * @param resourceIdName The unique identifier name (value of the name attribute) of the resource.
     * @return
     */
    private String searchAllResourcesValues(File valuesDir, String resourceType,
                                            String resourceIdName) {
        String value = null;
        Collection<File> resValueFiles = getXMLResourceFiles(valuesDir);
        for (File resFile : resValueFiles) {
            value = getResourceValue(resFile, resourceType, resourceIdName);
            if (!Strings.isNullOrEmpty(value)) {
                break;
            }
        }
        if (value !=null && value.startsWith("@")) {
            // Ignore multiple XML elements values for now.
            if (! value.contains(" ")) {
                try {
                    String resName = value.substring(value.indexOf("@") + 1, value.indexOf("/"));
                    value = searchAllResourcesValues(valuesDir, resName,
                            value.replace("@" + resName + "/", ""));
                } catch (IndexOutOfBoundsException e) {
                    logger.error("Failed to find the resource file for {}", value, e);
                }
            }
        }
        return StringEscapeUtils.escapeXml10(value);

    }


    /**
     * Returns all XML resource files in the given values directory
     *
     * @param valuesDir the values/ directory
     * @return a collection of the XML resource files in the given values directory
     */
    private Collection<File> getXMLResourceFiles(File valuesDir) {
        Collection<File> valuesFiles = FileUtils.listFiles(valuesDir,
                new String[]{"xml", "XML"}, false);
        if (valuesFiles != null && valuesFiles.size() > 0) {
            return valuesFiles;
        } else {
            logger.info("No XML resource files found in {}",
                    valuesDir.getAbsolutePath());
        }
        return null;
    }

}
