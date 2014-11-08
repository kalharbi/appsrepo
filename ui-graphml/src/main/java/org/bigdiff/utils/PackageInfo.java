package org.bigdiff.utils;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.SAXException;
import org.yaml.snakeyaml.Yaml;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.*;
import java.io.*;
import java.util.HashMap;
import java.util.Map;

/**
 * App Package Info
 */

public class PackageInfo {

    private final static Logger logger = LoggerFactory
            .getLogger(PackageInfo.class);

    public static String getPackageNameFromManifest(File androidManifesFile) {
        try {
            logger.info("Extracting package name from apktool.yaml file");
            DocumentBuilderFactory factory = DocumentBuilderFactory
                    .newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(androidManifesFile);
            XPathFactory xPathfactory = XPathFactory.newInstance();
            XPath xpath = xPathfactory.newXPath();
            XPathExpression packageNameExpr = xpath
                    .compile("string(/manifest/@package)");
            String packageName = (String) packageNameExpr.evaluate(doc,
                    XPathConstants.STRING);
            if (packageName != null && packageName != "") {
                return packageName;
            }
        } catch (XPathExpressionException e) {
            logger.error("Error: XPathExpressionException occurred while parsing AndroidManifest file: ", e);
        } catch (SAXException e) {
            logger.error("Error: SAXException occurred while parsing AndroidManifest file: ", e);
        } catch (IOException e) {
            logger.error("Error: IOException occurred while parsing AndroidManifest file: ", e);
        } catch (ParserConfigurationException e) {
            logger.error("Error: ParserConfigurationException occurred while parsing AndroidManifest file: ", e);
        }
        return null;
    }
    /**
     * Returns version name and version code values from AndroidManifest.xml.
     *
     * @param androidManifesFile
     * @return
     */
    public static HashMap<String, String> getVersionFromManifest(
            File androidManifesFile) {
        logger.info("Extracting version information from AndroidManifest.xml file");
        HashMap<String, String> appVersion = null;
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory
                    .newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(androidManifesFile);
            Element rootElement = doc.getDocumentElement();
            String versionCode = rootElement.getAttribute("android:versionCode");
            String versionName = rootElement.getAttribute("android:versionName");
            if (versionName != null && !versionName.isEmpty()
                    && versionCode != null && !versionCode.isEmpty()) {
                appVersion = new HashMap<String, String>();
                appVersion.put("versionName", versionName);
                appVersion.put("versionCode", versionCode);
            }
        } catch (SAXException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ParserConfigurationException e) {
            e.printStackTrace();
        }
        return appVersion;
    }

    /**
     * Returns version name and version code values from apktool.yaml.
     *
     * @param apktoolYamlFile apktool.yml file
     * @return @link{HashMap} object containing "versionName" and "versionCode"
     * keys
     */
    public static HashMap<String, String> getVersionFromYAMLFile(
            File apktoolYamlFile) {
        logger.info("Extracting version information from apktool.yaml file");
        HashMap<String, String> versionInfo = null;
        try {
            InputStream inputStream = new FileInputStream(apktoolYamlFile);
            Yaml yaml = new Yaml();
            @SuppressWarnings("unchecked")
            Map<String, Map<String, String>> values = (Map<String, Map<String, String>>) yaml
                    .load(inputStream);
            Map<String, String> versionKeyValues = values.get("versionInfo");
            if (versionKeyValues != null) {
                String versionName = versionKeyValues.get("versionName");
                String versionCode = versionKeyValues.get("versionCode");
                versionInfo = new HashMap<String, String>();
                versionInfo.put("versionName", versionName);
                versionInfo.put("versionCode", versionCode);
            }
            inputStream.close();
        } catch (FileNotFoundException e) {
            logger.error("Error: apktool Yaml file does not exist.");
        } catch (IOException e) {
            logger.error("Error: IOException while reading apktool Yaml file: ", e);
        }
        return versionInfo;
    }
}

