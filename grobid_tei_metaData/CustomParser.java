import org.apache.tika.exception.TikaException;
import org.apache.tika.io.TemporaryResources;
import org.apache.tika.io.TikaInputStream;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.mime.MediaType;
import org.apache.tika.parser.AbstractParser;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.journal.GrobidRESTParser;
import org.apache.tika.parser.pdf.PDFParser;
import org.xml.sax.ContentHandler;
import org.xml.sax.SAXException;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.Set;


public class CustomParser extends AbstractParser {

    /**
     * Generated serial ID
     */
    private static final long serialVersionUID = 4664255544154296438L;

    private static final MediaType TYPE = MediaType.application("pdf");

    private static final Set<MediaType> SUPPORTED_TYPES = Collections
            .singleton(TYPE);

    public Set<MediaType> getSupportedTypes(ParseContext context) {
        return SUPPORTED_TYPES;
    }

    public void parse(InputStream stream, ContentHandler handler,
                      Metadata metadata, ParseContext context) throws IOException,
            SAXException, TikaException {
        TikaInputStream tis = TikaInputStream.get(stream, new TemporaryResources());
        File tmpFile = tis.getFile();

        GrobidRESTParser grobidParser = new GrobidRESTParser();
        grobidParser.parse(tmpFile.getAbsolutePath(), handler, metadata, context);

        //PDFParser parser = new PDFParser();
        //parser.parse(new FileInputStream(tmpFile), handler, metadata, context);
    }


}