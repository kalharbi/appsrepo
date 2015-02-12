package org.bigdiff;

import org.junit.Before;

import java.io.File;
import java.io.IOException;
import static org.hamcrest.number.OrderingComparison.greaterThan;
import static org.hamcrest.MatcherAssert.assertThat;
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
    public void testGenerateGraphML() throws IOException {
        App app = new App();
        app.doGraphML(new File[]{apkDir});
        File uiGraphMLDir = new File(apkDir, "ui-graphml");
        graphmlFile = new File(uiGraphMLDir, package_name + "-" + version_code +
                ".graphml");
        assertTrue("Failed to create the graphml file " + graphmlFile.getAbsolutePath(),
                graphmlFile.exists());
        // The size of the graphml file for me.pou.app version_code 188 should be ~ 9.1 KB
        assertThat("GraphML " + graphmlFile.getAbsolutePath() + " is empty.",
                graphmlFile.length(),
                greaterThan(new Long(900)));
    }

}
