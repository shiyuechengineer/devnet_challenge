import csv
from webexteamssdk import WebexTeamsAPI
import meraki

meraki_api_key = '093b24e85df15a3e66f1fc359f4c48493eaa1b73'
mynetwork = 'L_646829496481100388'
org_id = '537758'

msversion = '11.31'
mrversion = '26.6.1'
mxversion = '15.27'
mvversion = '4.0'
WebexRoomID = "Y2lzY29zcGFyazovL3VzL1JPT00vNWJiMmRiZjAtNmFkOC0xMWVhLWEzNmEtMDc0ZjMxN2Y0Njli"
# myWebexToken = "" #you will need to put your personal token here

# Dictionary with Meraki product information & dictated firmware versions
products = {
    'Switches': {
        'prefix': ('MS'),
        'version': f'switch-{msversion.replace(".", "-")}',
    },
    'APs': {
        'prefix': ('MR'),
        'version': f'wireless-{mrversion.replace(".", "-")}',
    },
    'Security Appliances': {
        'prefix': ('MX', 'vM', 'Z1', 'Z3'),     # including vMX100 & Z1/Z3 teleworker gateways
        'version': f'wired-{mxversion.replace(".", "-")}',
    },
    'Cameras': {
        'prefix': ('MV'),
        'version': f'camera-{mvversion.replace(".", "-")}',
    },
}

# Meraki Python library @ github.com/meraki/dashboard-api-python
dashboard = meraki.DashboardAPI(meraki_api_key, output_log=False)
devices = dashboard.organizations.getOrganizationDevices(org_id)
net_devices = [d for d in devices if d['networkId'] == mynetwork]
nonstandard_devices = []

# Iterate through the four product families, tallying each family's devices running on specified firmware versions
for product, info in products.items():
    standard = [d for d in net_devices if d['model'][:2] in info['prefix'] and d['firmware'] == info['version']]
    nonstandard = [d for d in net_devices if d['model'][:2] in info['prefix'] and d['firmware'] != info['version']]
    print(f'Total {product} that meet standard: {len(standard)}')
    nonstandard_devices.extend(nonstandard)

# List devices that are not running specified firmware versions
print('Devices that will need to be manually checked:')
for d in nonstandard_devices:
    print(f'Serial#: {d["serial"]} , Model#: {d["model"]}')

# Write full org report to file
output_file = f'all_devices_{org_id}.csv'
field_names = set().union(*[d.keys() for d in devices])
with open(output_file, 'w') as fp:
    csv_writer = csv.DictWriter(fp, field_names)
    csv_writer.writeheader()
    csv_writer.writerows(devices)

# Post in Webex Teams
teams = WebexTeamsAPI(myWebexToken)
teams.messages.create(WebexRoomID, markdown='**Report Completed** 🎉', files=[output_file])
