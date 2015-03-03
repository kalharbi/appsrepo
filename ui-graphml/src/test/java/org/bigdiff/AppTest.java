package org.bigdiff;

import org.junit.Before;
import org.xml.sax.SAXException;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.number.OrderingComparison.greaterThan;
import static org.junit.Assert.*;


/**
 * Unit test for simple App.
 */
public class AppTest {
    private File apkDir = null;
    private String package_name = "me.pou.app";
    private String version_code = "188";
    private File graphmlFile = null;

    @Before
    public void setUp() throws IOException {
        apkDir = new File(getClass().getResource("apps" + File.separator +
                package_name + "-" + version_code).getPath());
        assertNotNull("The unpacked APK file is not found.", apkDir);
    }

    @org.junit.Test
    public void testGenerateGraphML() throws IOException, SAXException {
        App app = new App();
        app.doGraphML(new File[]{apkDir});
        File uiGraphMLDir = new File(apkDir, "ui-graphml");
        graphmlFile = new File(uiGraphMLDir, package_name + "-" + version_code +
                ".graphml");
        assertTrue("Failed to create the graphml file " + graphmlFile.getAbsolutePath(),
                graphmlFile.exists());
        // The generated GraphML file should be exactly the same as the manually verified file.
        File validGraphMLFile = new File(apkDir, "me.pou.app-188.graphml.valid");
        FileInputStream fis_expected = new FileInputStream(validGraphMLFile);
        String md5_validGraphMLFile = org.apache.commons.codec.digest.DigestUtils.md5Hex(fis_expected);
        fis_expected.close();
        FileInputStream fis_actual = new FileInputStream(graphmlFile);
        String md5_actualGraphMLFile = org.apache.commons.codec.digest.DigestUtils.md5Hex(fis_actual);
        fis_actual.close();
        assertEquals("The generated graphML is invalid. MD5 comparison failed.",
                md5_validGraphMLFile, md5_actualGraphMLFile);
    }

}
