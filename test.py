import re

custom_params = {}
medicine_titles = self.medsenger_api.get_records(contract.id, "hormonal_contraception_medicine", limit=1)
if medicine_titles:
    custom_params['title'] = medicine_titles[0]['value']

medicine_times = self.medsenger_api.get_records(contract.id, "hormonal_contraception_start_time", limit=1)
if medicine_times and re.match(r'\d\d:\d\d', medicine_times[0]['value']):
    custom_params['times'] = [medicine_times[0]['value']]

medicine_manager.attach(80, contract, custom_params)
