package org.bigdiff.utils;

import com.beust.jcommander.IStringConverter;

import java.io.File;

/**
 * A type converter that turns a string into a file.
 */
public class FileConverter implements IStringConverter<File> {
    @Override
    public File convert(String value) {
        return new File(value);
    }
}
