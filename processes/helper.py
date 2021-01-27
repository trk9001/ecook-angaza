import datetime, re
from typing import List
from angaza import Angaza
from .vars import ANGAZA_USERNAME, ANGAZA_PASSWORD


class Helper:
    def angaza(self) -> Angaza:
        """Initialize Angaza."""

        angaza = Angaza()
        angaza.set_auth(username=ANGAZA_USERNAME, password=ANGAZA_PASSWORD)

        return angaza

    def convert_to_datetime(self, item, format='%Y-%m-%dT%H:%M:%Sz') -> datetime:
        """Convert to python datetime object."""

        return datetime.datetime.strptime(item, format)

    def get_usage_data(self, unit_number: int, from_when_dt: str, to_when_dt: str=str(), offset: int = 0, variable = []) -> List:
        """Get usage data of the specified unit number from Angaza."""

        data = self.angaza().get_usage_data(
            unit_number=unit_number,
            from_when_dt=from_when_dt,
            offset=offset
        )

        if to_when_dt != '':
            data = self.angaza().get_usage_data(
                unit_number=unit_number,
                from_when_dt=from_when_dt,
                to_when_dt=to_when_dt,
                offset=offset
            )

        if '_embedded' in data and len(data['_embedded']['item']) > 0:
            variable += data['_embedded']['item']

            if '_links' in data and 'next' in data['_links']:
                link = data['_links']['next']['href']
                offset = re.search('&offset=(.*)', link)

                if offset and offset > 0:
                    if to_when_dt != '':
                        self.get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, to_when_dt=to_when_dt, offset=offset, variable=variable)
                    else:
                        self.get_usage_data(unit_number=unit_number, from_when_dt=from_when_dt, offset=offset, variable=variable)

        return variable
