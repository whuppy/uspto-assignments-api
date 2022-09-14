#!/usr/bin/python
import requests
from lxml import etree
import sys

try:
    myQuery = sys.argv[1]
except IndexError:
    print(f'Usage: {sys.argv[0]} query')
    sys.exit(1)

rows = 1000
rqstUrl = f'https://assignment-api.uspto.gov/patent/basicSearch?rows={rows}&query={myQuery}'
print(rqstUrl)
rsp = requests.get(rqstUrl)
print(rsp)


xml_ascii = rsp.text.encode('ascii')
rsproot = etree.fromstring(xml_ascii)
#rsproot = etree.parse('fake.xml')
rslt = rsproot.xpath('result')[0]

def spliceAssigneeAddress(addy_tuple):
    result = ''
    for adt in addy_tuple[1:]:
        if ('NULL' != adt):
            result = f'{result}{adt} '
    return result[:-1]

def parseDoc(d):
    '''
    Extract what we want from a <doc> Element and return it as a dict.
    '''
    result = {}
    
    result['last_updated'] = d.xpath('.//date[@name="lastUpdateDate"]/text()')[0]
    result['execution_date'] = d.xpath('.//date[@name="patAssignorEarliestExDate"]/text()')[0]
    result['assignor_names'] = d.xpath('.//arr[@name="patAssignorName"]/str/text()')

    result['invention_title'] =  d.xpath('.//arr[@name="inventionTitle"]/str/text()')
    result['inventors'] =  d.xpath('.//arr[@name="inventors"]/str/text()')
    result['application_number'] = d.xpath('.//arr[@name="applNum"]/str/text()')
    result['filing_date'] =  d.xpath('.//arr[@name="filingDate"]/date/text()')
    result['publication_number'] =  d.xpath('.//arr[@name="publNum"]/str/text()')
    result['publication_date'] =  d.xpath('.//arr[@name="publDate"]/date/text()')
    result['patent_number'] = d.xpath('.//arr[@name="patNum"]/str/text()')
    result['issue_date'] =  d.xpath('.//arr[@name="issueDate"]/date/text()')
    result['pct_number'] =  d.xpath('.//arr[@name="pctNum"]/str/text()')
    result['intl_publication_date'] =  d.xpath('.//arr[@name="intlPublDate"]/date/text()')
    
    correspondent_name = d.xpath('.//str[@name="corrName"]/text()')[0]
    correspondent_address_1 = d.xpath('.//str[@name="corrAddress1"]/text()')
    correspondent_address_2 = d.xpath('.//str[@name="corrAddress2"]/text()')
    correspondent_address_3 = d.xpath('.//str[@name="corrAddress3"]/text()')
    correspondent_address = ''
    for i in (correspondent_address_1, correspondent_address_2, correspondent_address_3):
        if ('NULL' != i):
            try:
                correspondent_address = f'{correspondent_address}{i[0]} '
            except IndexError:
                continue
    correspondent_address = correspondent_address[:-1]
    result['correspondent'] = (correspondent_name, correspondent_address)

    assignee_names = d.xpath('.//arr[@name="patAssigneeName"]/str/text()')
    assignee_address_1 = d.xpath('.//arr[@name="patAssigneeAddress1"]/str/text()')
    assignee_address_2 = d.xpath('.//arr[@name="patAssigneeAddress2"]/str/text()')
    assignee_city = d.xpath('.//arr[@name="patAssigneeCity"]/str/text()') 
    assignee_state = d.xpath('.//arr[@name="patAssigneeState"]/str/text()') 
    assignee_country = d.xpath('.//arr[@name="patAssigneeCountryName"]/str/text()') 
    assignee_postcode = d.xpath('.//arr[@name="patAssigneePostcode"]/str/text()') 
    zipped_assignee = list(zip(assignee_names, assignee_address_1, assignee_address_2, assignee_city, assignee_state, assignee_country, assignee_postcode))
    assignees = []
    for za in zipped_assignee:
        assignees.append((za[0], spliceAssigneeAddress(za)))
    result['assignees'] = assignees

    return result
    
doc_dicts = []
# Find and parse all 'doc' tags
for d in rslt.iter('doc'):
    doc_dicts.append(parseDoc(d))
    # end for loop.
print(f'doc_dicts created.')

for d in doc_dicts:
    print(f'{d}\n')
    