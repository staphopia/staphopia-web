FIELDS = {
    # Project Information
    'contact_name':['Contact Name', 'Alexander Ogston'],
    'contact_email':['Contact Email', 'usa300@staphopia.com'],
    'contact_link':['Contact Link', 'www.staphopia.com/contact/'],
    'sequencing_center':['Sequencing Center',  'Emory Integrated Genomics Core'],
    'sequencing_center_link':['Sequencing Center Link', 'eigc.emory.edu'],
    'sequencing_libaray_method':['Sequencing Library Method',  'Standard MinION protocol'],
    'sequencing_platform':['Sequencing Platform', 'Illumina MiSeq'],

    # Publication Inforamtion
    'funding_agency':['Funding Agency', 'NIH'],
    'funding_agency_link':['Funding Agency Link', 'www.nih.gov'],
    
    # Organism Information
    'isolation_country':['Isolation Country', 'United States'],
    'isolation_city':['Isolation City', 'Atlanta'],
    'isolation_region':['Isolation Region', 'Georgia'],

}

FIELD_ORDER = [
    #Project Information
    'contact_name',
    'contact_email',
    'contact_link',
    'sequencing_center',
    'sequencing_center_link',
    'sequencing_libaray_method',
    'sequencing_platform',

    #Publication Information
    'funding_agency',
    'funding_agency_link',

    #Organism Information
    'isolation_country',
    'isolation_city',
    'isolation_region',
]

SELECT_FIELDS = [
    'sequencing_platform',
]

CHOICES = {
    'sequencing_platform':(
        ('', 'Select One'),
        ('454 GS Junior', '454 GS Junior'),
        ('Illumina MiSeq', 'Illumina MiSeq'),
        ('Illumina HiSeq 2000', 'Illumina HiSeq 2000'),
        ('Illumina HiSeq 2500', 'Illumina HiSeq 2500'),
        ('Ion Torrent PGM', 'Ion Torrent PGM'),
        ('PacBio RS', 'PacBio RS'),
        ('', '--------------------'),
        ('454 GS 20', '454 GS 20'),
        ('454 GS FLX', '454 GS FLX'),
        ('454 GS FLX Titanium', '454 GS FLX Titanium'),
        ('454 GS FLX+', '454 GS FLX+'),
        ('Illumina Genome Analyzer', 'Illumina Genome Analyzer'),
        ('Illumina Genome Analyzer II', 'Illumina Genome Analyzer II'),
        ('Illumina Genome Analyzer IIx', 'Illumina Genome Analyzer IIx'),
        ('Illumina HiScanSQ', 'Illumina HiScanSQ'),
        ('Illumina HiSeq 1000', 'Illumina HiSeq 1000'),
        ('Illumina HiSeq 1500', 'Illumina HiSeq 1500'),
        ('Ion Torrent Proton', 'Ion Torrent Proton'),
        ('AB 310 Genetic Analyzer', 'AB 310 Genetic Analyzer'),
        ('AB 3130 Genetic Analyzer', 'AB 3130 Genetic Analyzer'),
        ('AB 3130xL Genetic Analyzer', 'AB 3130xL Genetic Analyzer'),
        ('AB 3500 Genetic Analyzer', 'AB 3500 Genetic Analyzer'),
        ('AB 3500xL Genetic Analyzer', 'AB 3500xL Genetic Analyzer'),
        ('AB 3730 Genetic Analyzer', 'AB 3730 Genetic Analyzer'),
        ('AB 3730xL Genetic Analyzer', 'AB 3730xL Genetic Analyzer'),
        ('AB 5500 Genetic Analyzer', 'AB 5500 Genetic Analyzer'),
        ('AB 5500xl Genetic Analyzer', 'AB 5500xl Genetic Analyzer'),
        ('AB SOLiD 3 Plus System', 'AB SOLiD 3 Plus System'),
        ('AB SOLiD 4 System', 'AB SOLiD 4 System'),
        ('AB SOLiD 4hq System', 'AB SOLiD 4hq System'),
        ('AB SOLiD PI System', 'AB SOLiD PI System'),
        ('AB SOLiD System 1.0', 'AB SOLiD System 1.0'),
        ('AB SOLiD System 2.0', 'AB SOLiD System 2.0'),
        ('AB SOLiD System 3.0', 'AB SOLiD System 3.0'),
        ('Complete Genomics', 'Complete Genomics'),
        ('Helicos HeliScope', 'Helicos HeliScope'),
    ),
}