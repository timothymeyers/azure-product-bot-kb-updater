from azure_data_scraper.az_product_info import AzProductInfo
from azure.cognitiveservices.knowledge.qnamaker.models import (QnADTO, MetadataDTO)

FUNC_TEST_NUM = "0004"


def list_to_markdown(in_list=None, one_line=False) -> str:
    if in_list is None or in_list == []: return ""

    if len(in_list) == 1: return in_list[0] + "."

    # for long lists, force it to output a single line
    if len(in_list) > 3: one_line = True

    if one_line:
        return "\\n * %s \\n\\n" % str(in_list).replace('[', '').replace(']', '').replace('\'', '')

    a = ""
    for item in in_list:
        a = a + "\\n * %s" % item

    a = a + "\\n\\n"
    return a


class QnABruteForce:
    def __init__(self, az=AzProductInfo()):
        self.__az = az
        self.__qna = []

        self.__hydrate_qna()

    def qna(self):
        return self.__qna

    def dump_qna(self):

        for q, a in self.__qna:
            print(q, "\t", a)

    def __hydrate_qna(self):
        for id in self.__az.products_list():
            self.__hydrate_available_qna(id)
            self.__hydrate_preview_qna(id)
            self.__hydrate_expected_qna(id)

    def __hydrate_available_qna(self, id):
        md = [{
            'name': 'product',
            'value': id.replace('|', ' ').replace(':', ' ')
        }, {
            'name': 'questionType',
            'value': 'availability'
        }, {
            'name': 'functiontest',
            'value': FUNC_TEST_NUM
        }]

        ## answer 1
        # a = self.answer_is_ga(id)
        a = id + self.answer_where_ga(id)
        a_id = len(self.__qna)
        qs = [
            "Is %s ga?" % id, 
            "Is %s available?" % id,
            "What regions is %s available in?" % id,
            "What regions is %s ga in?" % id,
            "Where is %s ga in?" % id,
            "Where is %s available in?" % id,
            "Where is %s?" % id,
        ]

        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Availability Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 2
        # a = self.answer_is_ga_in_cloud(id, 'azure-public')
        a = id + self.answer_where_ga_in (id, 'azure-public')
        a_id = len(self.__qna)
        qs = [
            "Is %s available in Azure Commercial?" % id, 
            "Is %s GA in Azure Commercial?" % id,
            "Is %s ga in Azure Commercial?" % id,
            "Is %s in Azure Commercial?" % id,
            "What regions is %s available in Azure Commercial?" % id,
            "What regions is %s ga in Azure Commercial?" % id,
            "Where is %s available in Azure Commerical?" % id,
            "Where is %s ga in Azure Commerical?" % id,
            "Where is %s in Azure Commerical?" % id,
        ]
        md = md.copy()
        md.append({'name': 'cloud', 'value': 'azure-public'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Availability Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 3
        # a = self.answer_is_ga_in_cloud(id, 'azure-government')
        a = id + self.answer_where_ga_in(id, 'azure-government')
        a_id = len(self.__qna)
        qs = [
            "Is %s available in Azure Government?" % id,
            "Is %s GA in Azure Government?" % id,
            "Is %s available in MAG?" % id,
            "Is %s GA in MAG?" % id,
            "Is %s in Azure Government?" % id,
            "Is %s in MAG?" % id,
            "What regions is %s available in Azure Government?" % id,
            "What regions is %s ga in Azure Government?" % id,
            "Where is %s available in Azure Government?" % id,
            "Where is %s ga in Azure Government?" % id,
            "Where is %s in Azure Government?" % id,
            "What regions is %s available in MAG?" % id,
            "What regions is %s ga in MAG?" % id,
            "Where is %s available in MAG?" % id,
            "Where is %s ga in MAG?" % id,
            "Where is %s in MAG?" % id,
        ]
        md = md.copy()
        md.pop()
        md.append({'name': 'cloud', 'value': 'azure-government'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Availability Answers',
            'questions': qs,
            'metadata': md
        })

    def __hydrate_preview_qna(self, id):

        md = [{
            'name': 'product',
            'value': id.replace('|', ' ').replace(':', ' ')
        }, {
            'name': 'questionType',
            'value': 'preview'
        }, {
            'name': 'functiontest',
            'value': FUNC_TEST_NUM
        }]

        ## answer 1
        a = id + self.answer_where_preview(id)
        a_id = len(self.__qna)
        qs = ["Is %s in preview?" % id, "Where is %s in preview?" % id]

        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Preview Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 2
        a = id + self.answer_where_preview_in(id, 'azure-public')
        a_id = len(self.__qna)
        qs = [
            "Is %s in preview in Azure Commercial?" % id,
            "Where is %s in preview in Azure Commercial?" % id
        ]
        md = md.copy()
        md.append({'name': 'cloud', 'value': 'azure-public'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Preview Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 3
        a = id + self.answer_where_preview_in(id, 'azure-government')
        a_id = len(self.__qna)
        qs = [
            "Is %s in preview in Azure Government?" % id,
            "Where is %s in preview in Azure Government?" % id,
            "Is %s in preview in MAG?" % id,
            "Where is %s in preview in MAG?" % id,
        ]
        md = md.copy()
        md.pop()
        md.append({'name': 'cloud', 'value': 'azure-government'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Preview Answers',
            'questions': qs,
            'metadata': md
        })

    def __hydrate_expected_qna(self, id):

        md = [{
            'name': 'product',
            'value': id.replace('|', ' ').replace(':', ' ')
        }, {
            'name': 'questionType',
            'value': 'ga-expected'
        }, {
            'name': 'functiontest',
            'value': FUNC_TEST_NUM
        }]

        ## answer 1
        a = id + self.answer_where_expected_ga(id)
        a_id = len(self.__qna)
        qs = ["When is %s expected to be available?" % id, "When is %s expected to be ga?" % id]

        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Expected Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 2
        a = id + self.answer_where_expected_ga_in(id, 'azure-public')
        a_id = len(self.__qna)
        qs = [
            "When is %s expected to be available in Azure Commercial?" % id,
            "When is %s expected to be ga in Azure Commercial?" % id
        ]
        md = md.copy()
        md.append({'name': 'cloud', 'value': 'azure-public'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Expected Answers',
            'questions': qs,
            'metadata': md
        })

        ## answer 3
        a = id + self.answer_where_expected_ga_in(id, 'azure-government')
        a_id = len(self.__qna)
        qs = [
            "When is %s expected to be available in Azure Government?" % id,
            "When is %s expected to be available in MAG?" % id,
            "When is %s expected to be ga in Azure Government?" % id,
            "When is %s expected to be ga in MAG?" % id
        ]
        md = md.copy()
        md.pop()
        md.append({'name': 'cloud', 'value': 'azure-government'})
        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': 'Expected Answers',
            'questions': qs,
            'metadata': md
        })

    def answer_is_ga(self, id):
        az_pub = self.__az.isProductAvailable(id, 'azure-public')
        az_gov = self.__az.isProductAvailable(id, 'azure-government')

        if (az_pub and az_gov):
            return "Yes. **%s** is GA in both *Azure Commercial* and *Azure Government*.\\nIt%s\\nIt%s" % (
                id, self.answer_where_ga_in(id, 'azure-public'),
                self.answer_where_ga_in(id, 'azure-government')
            )
        elif az_pub:
            return "Yes, only in *Azure Commercial* though. **%s**%s" % (
                id, self.answer_where_ga_in(id, 'azure-public')
            )
        elif az_gov:
            return "Yes, only in *Azure Government* though. **%s**%s" % (
                id, self.answer_where_ga_in(id, 'azure-government')
            )

        return "No. **%s**%s\\nAnd, it%s" % (
            id, self.answer_where_ga_in(id, 'azure-public'),
            self.answer_where_ga_in(id, 'azure-government')
        )

    def answer_is_ga_in_cloud(self, id, cloud):
        available = self.__az.isProductAvailable(id, cloud)

        if available:
            return "Yes. **%s**%s" % (id, self.answer_where_ga_in(id, cloud))
        return "No. **%s**%s" % (id, self.answer_where_ga_in(id, cloud))

    def answer_where_ga(self, id):
        return (
            self.answer_where_ga_in(id, 'azure-public') + '\\n\\n' + 'It' +
            self.answer_where_ga_in(id, 'azure-government')
        )

    def answer_where_ga_in(self, id, cloud):
        cloud_name = self.__cloud_name(cloud)
        regions = self.__az.getProductAvailableRegions(id, cloud)

        # return regions
        if len(regions) > 0:
            return " is GA in %s in: %s" % (cloud_name, list_to_markdown(regions))

        # it is not GA, check preview regions and expected release date

        ans = " is not currently GA in %s. " % (cloud_name)

        preview = self.answer_where_preview_in(id, cloud)
        preview = "However, it" + preview

        if "is not" not in preview:
            ans = ans + "\\n\\n" + preview

        expected = self.answer_where_expected_ga_in(id, cloud)
        expected = "It" + expected

        if "is not" not in expected:
            ans = ans + "\\n\\n" + expected

        return ans

    def answer_where_preview(self, id):
        az_pub = self.answer_where_preview_in(id, 'azure-public')
        az_gov = self.answer_where_preview_in(id, 'azure-government')

        if ("not" in az_pub and "not" in az_gov):
            return " is not in preview in either *Azure Commercial* or *Azure Government*"
        elif ("not" in az_pub):
            return az_gov + " However, it" + az_pub
        elif ("not" in az_gov):
            return az_pub + " However, it" + az_gov

        return (
            " is ***In Preview*** in *both* Azure Commercial and Azure Government.\\n\\n" + "It" +
            az_pub + "\\n\\n" + "It" + az_gov
        )

    def answer_where_preview_in(self, id, cloud):
        cloud_name = self.__cloud_name(cloud)
        regions = self.__az.getProductPreviewRegions(id, cloud)

        if len(regions) > 0:
            return " is ***In Preview*** in %s in: %s" % (cloud_name, list_to_markdown(regions))

        return " is not in preview in %s" % cloud_name

    def answer_where_expected_ga(self, id):
        az_pub = self.answer_where_expected_ga_in(id, 'azure-public')
        az_gov = self.answer_where_expected_ga_in(id, 'azure-government')

        if ("not" in az_pub and "not" in az_gov):
            return " is not targeted for either *Azure Commercial* or *Azure Government*"
        elif ("not" in az_pub):
            return az_gov + " However, it" + az_pub
        elif ("not" in az_gov):
            return az_pub + " However, it" + az_gov

        return (az_pub + "\\n\\n" + "It" + az_gov)

    def answer_where_expected_ga_in(self, id, cloud):
        ans = ""
        cloud_name = self.__cloud_name(cloud)
        available = self.__az.isProductAvailable(id, cloud)
        expected_ga = self.__az.getProductRegionsGATargets(id, cloud)

        if available:
            regions_ga = list_to_markdown(self.__az.getProductAvailableRegions(id, cloud))
            ans = " is already GA in %s in %s. " % (cloud_name, regions_ga)

            if (len(expected_ga) == 0):
                return ans

            ans = ans + "It"

        if (len(expected_ga) > 0):
            pretty_expected = self.__pretty_expected_list(expected_ga)
            return ans + " is currently targeted for GA in %s: %s" % (
                cloud_name, list_to_markdown(pretty_expected)
            )

        return " is not currently scheduled for GA in %s. " % cloud_name

    """
    def __answer_is_preview(self, id):
       

        return

    def __answer_is_preview_in_region(self, id, region):
        # getProductPreviewRegions(self, prod, cloud="") -> list:
        return

    def __answer_is_expected_ga(self, id):
        # getProductRegionsGATargets
        return

    def __answer_is_expected_ga_in_region(self, id, region):
        # getProductRegionsGATargets
        return
    """

    def __cloud_name(self, cloud) -> str:
        if (cloud == 'azure-public'): return "*Azure Commercial*"
        if (cloud == 'azure-government'): return "*Azure Government*"

        raise Exception("Unknown cloud", cloud)

    def __pretty_expected_list(self, in_list):
        return [i['region'] + " (" + i['ga-expected'] + ")" for i in in_list]

    def dump(self):
        return self.__az.product_list()

    ##########################

    def qnaGetAvailable(self):

        for id, prod in self.__joined_data.items():

            svc = ""
            if 'service' in prod.keys():
                svc = prod['service']

            q = "What scopes is %s available at? \t" % id
            print(q, self.answer_whatScopes(id, prod))
            q = "What scopes is %s available at in Azure Commercial? \t" % id
            print(q, self.answer_whatScopesIn(id, "Azure Commercial", prod['azure-public'], svc))
            q = "What scopes is %s available at in Azure Government? \t" % id
            print(
                q, self.answer_whatScopesIn(id, "Azure Government", prod['azure-government'], svc)
            )

        return {}

    """
    Is XXX available?
    Is XXX ga?
    Is XXX ga in Azure Government?
    Is XXX ga in Azure Commercial?
    Is XXX available in Azure Government?
    Is XXX available in Azure Commercial?
    """

    def answer_isGa(self, id, prod):
        azpub = prod['azure-public']['available']
        azgov = prod['azure-government']['available']

        if (azpub and azgov):
            return (
                "**%s** is in both Azure Commercial and Azure Government.\\n\\n" % id +
                self.answer_whatRegionsGaIn(id, "Azure Commercial", prod['azure-public']) +
                "\\n\\n" +
                self.answer_whatRegionsGaIn(id, "Azure Government", prod['azure-government'])
            )
        elif azpub:
            return (
                "**%s** is available in Azure Commercial, but not Azure Government.\\n\\n" % id +
                self.answer_whatRegionsGaIn(id, "Azure Commercial", prod['azure-public'])
            )
        elif azgov:
            return (
                "**%s** is available in Azure Government, but not Azure Commercial.\\n\\n" % id +
                self.answer_whatRegionsGaIn(id, "Azure Government", prod['azure-government'])
            )

        # return "**%s** is not available in either Azure Commercial or Azure Government" % id
        return (
            self.answer_whatRegionsGaIn(id, "Azure Commercial", prod['azure-public']) + "\\n\\n" +
            self.answer_whatRegionsGaIn(id, "Azure Government", prod['azure-government'])
        )

    def answer_isGaIn(self, id, cloud_name, cloud_json):
        if cloud_json['available']:
            return ("Yes. " + self.answer_whatRegionsGaIn(id, cloud_name, cloud_json))

        return self.answer_whatRegionsGaIn(id, cloud_name, cloud_json)

    """
    When is XXX expected to be available?
    When is XXX expected to be available in Azure Government?
    When is XXX expected to be available in Azure Commercial?
    """

    def answer_isExpectedToBeGa(self, id, prod):
        return (
            self.answer_isExpectedToBeGaIn(id, "Azure Commercial", prod['azure-public']) +
            "\\n\\n" +
            self.answer_isExpectedToBeGaIn(id, "Azure Government", prod['azure-government'])
        )

    def answer_isExpectedToBeGaIn(self, id, cloud_name, cloud_json):
        avail = cloud_json['available']
        exp = cloud_json['planned-active']
        a = ""

        if avail:
            a = "**%s** is already available in *%s* in %s" % (
                id, cloud_name, list_to_markdown(cloud_json['ga'])
            )

        if avail and len(exp) == 0:
            return a
        if len(exp) > 0:
            return (
                a + "\\n\\n"
                "GA for **%s** in *%s* is currently targeted for: %s" %
                (id, cloud_name, list_to_markdown(exp))
            )

        return "**%s** is not currently scheduled for GA in *%s*. " % (id, cloud_name)

    """
    What regions are XXX available in?
    What regions are XXX available in Azure Commercial?
    What regions are XXX available in Azure Government?
    """

    def answer_whatRegionsGa(self, id, prod):
        return (
            self.answer_whatRegionsGaIn(id, "Azure Commercial", prod['azure-public']) + "\\n\\n" +
            self.answer_whatRegionsGaIn(id, "Azure Government", prod['azure-government'])
        )

    def answer_whatRegionsGaIn(self, id, cloud_name, cloud_json):
        regions = cloud_json['ga']
        preview = cloud_json['preview']

        if len(regions) > 0:
            return "**%s** is GA in *%s* in: %s" % (id, cloud_name, list_to_markdown(regions))
        else:
            a = "**%s** is not currently GA in *%s*. " % (id, cloud_name)

            if len(preview) > 0:
                a = a + \
                    " However, it is ***in preview*** in %s" % list_to_markdown(
                        preview)

            return a + self.answer_isExpectedToBeGaIn(id, cloud_name, cloud_json)

    """
    Is XXX in preview?
    Is XXX in preview in Azure Government?
    Is XXX in preview in Azure Commercial?
    """

    def answer_isPreview(self, id, prod):
        return (
            self.answer_isPreviewIn(id, "Azure Commercial", prod['azure-public']) + "\\n\\n" +
            self.answer_isPreviewIn(id, "Azure Government", prod['azure-government'])
        )

    def answer_isPreviewIn(self, id, cloud_name, cloud_json):
        avail = cloud_json['available']
        preview = cloud_json['preview']
        a = ""

        if avail:
            a = "**%s** is already available in *%s* in %s" % (
                id, cloud_name, list_to_markdown(cloud_json['ga'])
            )

        if avail and len(preview) == 0:
            return a
        if len(preview) > 0:
            return (
                a + "\\n\\n"
                "**%s** is in preview in *%s* in %s" % (id, cloud_name, list_to_markdown(preview))
            )

        return "**%s** is not currently in preview in *%s*. " % (id, cloud_name)

    """
    What scopes is XXX available at?
    What scopes is XXX available at in Azure Commercial?
    What scopes is XXX available at in Azure Government?
    """

    def answer_whatScopes(self, id, prod):
        if 'service' in prod.keys():
            return (
                self.
                answer_whatScopesIn(id, "Azure Commercial", prod['azure-public'], prod['service']) +
                "\\n\\n" + self.answer_whatScopesIn(
                    id, "Azure Government", prod['azure-government'], prod['service']
                )
            )

        return (
            self.answer_whatScopesIn(id, "Azure Commercial", prod['azure-public']) + "\\n\\n" +
            self.answer_whatScopesIn(id, "Azure Government", prod['azure-government'])
        )

    def answer_whatScopesIn(self, id, cloud_name, cloud_json, svc=""):
        scopes = cloud_json['scopes']

        if len(scopes) > 0:
            return "In *%s*, **%s** is available at %s" % (cloud_name, id, list_to_markdown(scopes))

        else:
            a = "I don't have any audit scope or impact level information about **%s** in *%s*. " % (
                id, cloud_name
            )

            if svc != "":
                if (cloud_name.__contains__("ov") or cloud_name.__contains__("MAG")):
                    svc_json = self.__joined_data[svc]['azure-government']
                else:
                    svc_json = self.__joined_data[svc]['azure-public']

                return (
                    a + " However, it is a capability of %s. " % svc +
                    "Here is what I know about *%s*'s audit scopes and impact levels:\\n\\n" % svc +
                    self.answer_whatScopesIn(svc, cloud_name, svc_json)
                )

            return a

    """
    Is %s at %s?
    Is %s at %s in %s?
    """

    def qnaGetScope(self):

        for id in (maps.service_list + maps.capability_list):
            for scope in (maps.us_scopes + maps.usgov_scopes):
                if not scope.__contains__("Il5"):
                    print(
                        "Is %s at %s? \t" % (id, maps.scope_map[scope]),
                        self.answer_isAtScope(id, scope)
                    )

            # Special IL5 Use Case
            print("Is %s at IL5? \t" % id, self.answer_isAtIL5(id))

        return

    def answer_isAtScope(self, id, scope):

        if (id in self.__scope_lookup[scope]):
            return "Yes. **%s** is %s" % (id, maps.scope_map[scope])

        return "No. **%s** is not at %s yet" % (id, maps.scope_map[scope])

    def answer_isAtIL5(self, id):
        # 'dodCcSrgIl5AzureGov': 'IL5 in Gov Regions',
        # 'dodCcSrgIl5AzureDod': 'IL5 in DoD Regions',
        gov = id in self.__scope_lookup['dodCcSrgIl5AzureGov']
        dod = id in self.__scope_lookup['dodCcSrgIl5AzureDod']

        if (gov and dod):
            return "Yes, **%s** is IL5 in ***both*** Gov and DoD regions" % id
        if (gov):
            return "Yes. However, **%s** is IL5 ***in Gov regions only***." % id
        if (dod):
            return "Yes. However, **%s** is IL5 ***in DoD regions only***." % id

        return "No. **%s** is not at IL5 yet" % id

    def qnaGetRegions(self):
        for id in (maps.service_list + maps.capability_list):
            for region in (maps.us_regions + maps.usgov_regions + maps.usdod_regions):
                if not region.__contains__("non-regional"):
                    print("Is %s in %s? \t" % (id, region), self.answer_isInRegion(id, region))

    def answer_isInRegion(self, id, region):

        if id in self.__region_lookup[region]:
            return "Yes. **%s** is in %s" % (id, region)

        if region in maps.us_regions:
            if id != "non-regional" and id in self.__region_lookup['non-regional']:
                return "Yes. **%s** is in %s. It is *Non-Regional* in Azure Commercial." % (
                    id, region
                )
            else:
                return self.answer_whatRegionsGaIn(
                    id, "Azure Commercial", self.__joined_data[id]['azure-public']
                )

        if region in maps.usgov_regions:
            if id != "usgov-non-regional" and id in self.__region_lookup['usgov-non-regional']:
                return "Yes. **%s** is in %s. It is *Non-Regional* in Azure Government." % (
                    id, region
                )
            else:
                return self.answer_whatRegionsGaIn(
                    id, "Azure Government", self.__joined_data[id]['azure-government']
                )

        return "No. **%s** is not in %s yet. And, I'm confused by the question." % (id, region)


"""
What can you tell me about XXX?"

What is available in XXX region?

What is available at XXX scope?
What is available at XXX scope in Azure Commercial?
What is available at XXX scope in Azure Government?
"""
