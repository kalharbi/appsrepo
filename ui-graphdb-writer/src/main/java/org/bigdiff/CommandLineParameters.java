package org.bigdiff;

import com.beust.jcommander.Parameter;
import org.bigdiff.utils.FileConverter;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by Khalid on 11/6/14.
 */
public class CommandLineParameters {

    // Command Line Parameters/Arguments
    @Parameter(description = "unpacked_apks_path", arity = 1)
    public List<String> parameters = new ArrayList<String>();

    @Parameter(names = {"-h", "-help"}, description = "print help and exit.", help = true)
    public boolean help;

    @Parameter(names = {"-v", "-version"}, description = "Prints version and exit")
    public boolean version;

    @Parameter(names = {"-b", "-db-path"}, description = "the location of neo4j's database directory.",
            required = true, converter = FileConverter.class)
    public File dbDir;

    @Parameter(names = {"-l", "-log"}, description = "Write error level logs to DIR.", converter = FileConverter.class)
    public File logFile;
}
