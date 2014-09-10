/**
Khalid
 */
package org.sikuli.apps.utils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Document;
import org.xml.sax.SAXException;
import org.yaml.snakeyaml.Yaml;

public class PackageInfo {

	private final static Logger logger = LoggerFactory
			.getLogger(PackageInfo.class);

	public static String getPackageNameFromManifest(File androidManifesFile) {
		try {
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

	/**
	 * Returns version name and version code values from AndroidManifest.xml.
	 * 
	 * @param androidManifesFile
	 * @return
	 */
	public static HashMap<String, String> getVersionFromManifest(
			File androidManifesFile) {
		HashMap<String, String> appVersion = null;
		try {

			DocumentBuilderFactory factory = DocumentBuilderFactory
					.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();
			Document doc = builder.parse(androidManifesFile);
			XPathFactory xPathfactory = XPathFactory.newInstance();
			XPath xpath = xPathfactory.newXPath();
			XPathExpression versionCodeExpr = xpath
					.compile("string(/manifest/@android:versionCode)");
			String versionCode = (String) versionCodeExpr.evaluate(doc,
					XPathConstants.STRING);
			XPathExpression versionNameExpr = xpath
					.compile("string(/manifest/@android:versionName)");
			String versionName = (String) versionNameExpr.evaluate(doc,
					XPathConstants.STRING);
			if (versionName != null && !versionName.isEmpty()
					&& versionCode != null && !versionCode.isEmpty()) {
				appVersion = new HashMap<String, String>();
				appVersion.put("versionName", versionName);
				appVersion.put("versionCode", versionCode);
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
		return appVersion;
	}

	/**
	 * Returns version name and version code values from apktool.yaml.
	 * 
	 * @param apktool
	 *            apktool.yml file
	 * @return @link{HashMap} object containing "versionName" and "versionCode"
	 *         keys
	 */
	public static HashMap<String, String> getVersionFromYAMLFile(
			File apktoolYamlFile) {
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
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return versionInfo;
	}
}
