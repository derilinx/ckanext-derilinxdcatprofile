from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS
from ckanext.dcat.profiles import RDFProfile

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace('http://schema.org/')
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

class DerilinxDCATAPProfile(RDFProfile):
        '''
        An RDF profile for Derilinx portals for expanded DCAT-AP export
        It requires the European DCAT-AP profile (`euro_dcat_ap`)
        '''

        def parse_dataset(self, dataset_dict, dataset_ref):
            return dataset_dict

        def graph_from_dataset(self, dataset_dict, dataset_ref):

            g = self.g
            temporaldone = spatialdone = contactdone = False
            temporal_text = self._get_dataset_value(dataset_dict, 'temporal')
            spatial_text = self._get_dataset_value(dataset_dict, 'spatial_other')
            telephone_text = self._get_dataset_value(dataset_dict, 'contact_phone')
            license_url = self._get_dataset_value(dataset_dict, 'license_url')
            rights_text = self._get_dataset_value(dataset_dict, 'rights')

            for dataset in g.subjects(RDF.type, DCAT.Dataset):
                for r in g[dataset]:
                    if r[0] == DCT.temporal:
                        temporaldone = True
                        if temporal_text:
                            g.add((r[1], RDFS.label, Literal(temporal_text)))
                    elif r[0] == DCT.spatial:
                        spatial_done = True
                        if spatial_text:
                            g.add((r[1], RDFS.label, Literal(spatial_text)))
                    elif r[0] == DCAT.contactPoint:
                        contactdone = True
                        if telephone_text:
                            g.add((r[1], VCARD.hasTelephone, Literal(telephone_text)))
                    #For some strange reason CKAN doesn't export license
                    #Also, rights are expected under the resource, we store them under dataset
                    elif r[0] == DCAT.distribution:
                        if license_url:
                            license_ref = URIRef(license_url)
                            g.add((license_ref, RDF.type, DCT.LicenseDocument))
                            g.add((r[1], DCT.license, license_ref))
                        if rights_text:
                            rights_ref = BNode()
                            g.add((rights_ref, RDF.type, DCT.RightsStatement))
                            g.add((r[1], DCT.rights, rights_ref))
                            g.add((rights_ref, SKOS.prefLabel, Literal(rights_text)))
            
            if not temporaldone and temporal_text:
                temporal_extent = BNode()                   
                g.add((temporal_extent, RDFS.label, Literal(temporal_text)))
                g.add((dataset_ref, DCT.temporal, temporal_extent))

            if not spatialdone and spatial_text:
                spatial_ref = BNode()
                g.add((spatial_ref, RDF.type, DCT.Location))
                g.add((dataset_ref, DCT.spatial, spatial_ref))
                g.add((spatial_ref, SKOS.prefLabel, Literal(spatial_text)))

            if not contactdone and telephone_text:
                contact_details = BNode()
                g.add((contact_details, RDF.type, VCARD.Organization))
                g.add((dataset_ref, DCAT.contactPoint, contact_details))
                g.add((contact_details, VCARD.hasTelephone, Literal(telephone_text)))

