doi/
utility.py : used to generate absolute path of files in specified directory

combine_json/
	Utility to combine sweet concepts, measurement extractions, doi generated, grobid header metadata extractions and related publications from google scholar api

grobid_tei_metaData/
	TEI_MetaData.java : Parser to extract TEI annotations
	errorFiles.txt	  : files names which failed to fetch TEI metadata
	logs.txt		  : failure logs captured
	CustomParser.java : Can be used if required to extract only Grobid metadata
	try/			  : input for sample test cases
	try_out/		  : output for sample test cases
	
scholar/
	doi/doi.txt		  	: generated doi for all files
	grobid_input_files 	: sample json input files which have grobid TEI metadata
	fetchScholar.py   	: python utility  which processes input from grobid_input_files/ to produce grobid_doi_scholar_output/
	grobid_doi_scholar_output : sample json output files which have combined grobid TEI metadata, doi, and related Publications
	scholar.py		  :	 adapted to support result in json format

solr/
	index_input_files/ 	: sample input json files for indexing
	schema.xml			: solr schema
	solrconfig.xml		: solr config file
	
memex_geoParser/
	views.py		  : id was changed to doi, as doi was used in Solr as unique field
	memex.png		  : snapshot of 44364 point locations plotted
	
d3_visualization/
	input json files and html code to generate viz
	d3_visualization/results/	
	Snapshots of visualization
