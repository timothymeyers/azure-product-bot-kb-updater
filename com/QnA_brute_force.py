from azure_data_scraper.az_product_info import AzProductInfo
from azure.cognitiveservices.knowledge.qnamaker.models import (QnADTO, MetadataDTO)

FUNC_TEST_NUM = "0006"
QnA_SOURCE = "QnA Brute Force"


def list_to_markdown(in_list=None, one_line=False) -> str:
    if in_list is None or in_list == []: return ""

    if len(in_list) == 1: return in_list[0] + "."

    # for long lists, force it to output a single line
    if len(in_list) > 3: one_line = True

    if one_line:
        return "\n * %s \n\n" % str(in_list).replace('[', '').replace(']', '').replace('\'', '')

    a = ""
    for item in in_list:
        a = a + "\n * %s" % item

    a = a + "\n\n"
    return a

# yapf: disable
# markdown helpers
def _b(text): return f"**{text}**"
def _i(text): return f"*{text}*"
# yapf: enable

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
        self.__hydrate_summary_info()

        for id in self.__az.products_list():
            ids_scopes = self.__hydrate_scopes_qna(id)
            self.__hydrate_available_qna(id, ids_scopes)
            self.__hydrate_preview_qna(id)
            self.__hydrate_expected_qna(id)
            

    def __hydrate_summary_info(self):
        md = [{
            'name': 'questionType',
            'value': 'summary'
        }, {
            'name': 'functiontest',
            'value': FUNC_TEST_NUM
        }]

        ## answer 1
        a = self.__answer_what_services()
        a_id = len(self.__qna)
        qs = ["What services do you know about?"]

        self.__qna.append({
            'id': a_id,
            'answer': a,
            'source': QnA_SOURCE,
            'questions': qs,
            'metadata': md
        })

    def __hydrate_available_qna(self, id, ids_scopes):
        # yapf: disable

        md_prod = {'name': 'product', 'value': id.replace('|', ' ').replace(':', ' ')}
        md_type = {'name': 'questionType', 'value': 'availability-quesiton'}
        md_test = {'name': 'functiontest', 'value': FUNC_TEST_NUM}
        md_azpub = {'name': 'cloud', 'value': 'azure-public'}
        md_azgov = {'name': 'cloud', 'value': 'azure-government'}

        md = [md_prod, md_type, md_test]
        
        ## Is {id} available?
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_ga(id),
            'source': QnA_SOURCE,
            'questions': 
                [ f"Is {id} {word}?" for word in ['ga','GA','available'] ] +
                [ f"What regions is {id} {word} in?" for word in ['ga','GA','available'] ] +
                [ f"Where is {id} {word}?" for word in ['ga in','GA in','available in', '' ] ],
            'metadata': md.copy(),
            'context': {
                'isContextOnly': False,
                'prompts':  self.__helper_get_scope_prompt (id, ids_scopes[0])
            }
        })

        ## answer 2
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_ga_in(id, 'azure-public'),
            'source': QnA_SOURCE,
            'questions': [ 
                f"{prefix} {id} {word} in {cloud_name}" 
                    for prefix in ['Is', 'What regions is', 'Where is']
                    for word in ['available', 'GA', 'ga', ''] 
                    for cloud_name in ['Azure Commercial', 'Azure Public', 'Commercial', 'Public', 'Pub', 'GCC']  
                ],
            'metadata': md + [ md_azpub ],
            'context': {
                'isContextOnly': False,
                'prompts': self.__helper_get_scope_prompt (id, ids_scopes[1], 'azure-public')
                
            }
        })

        ## answer 3    
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_ga_in(id, 'azure-government'),
            'source': QnA_SOURCE,
            'questions': [ 
                f"{prefix} {id} {word} in {cloud_name}" 
                    for prefix in ['Is', 'What regions is', 'Where is']
                    for word in ['available', 'GA', 'ga', ''] 
                    for cloud_name in ['Azure Government', 'Gov', 'MAG']  
                ],
            'metadata': md + [ md_azgov ],
            'context': {
                'isContextOnly': False,
                'prompts': self.__helper_get_scope_prompt (id, ids_scopes[2], 'azure-government')
            
            }
        })

        # yapf: enable

    def __helper_get_scope_prompt (self, id, id_scope, cloud=""):
        scope_list = self.__az.getProductScopes(id, cloud)

        if (len(scope_list) > -1):  # use this pattern for other follow-up questions that you want to skip; change this to 0
            return [{
                'DisplayOrder': 1,
                'DisplayText': "at which scopes / impact levels?",
                'QnaId': id_scope
            }]
        
        return []

    def __hydrate_preview_qna(self, id):

        # yapf: disable

        md_prod = {'name': 'product', 'value': id.replace('|', ' ').replace(':', ' ')}
        md_type = {'name': 'questionType', 'value': 'preview-quesiton'}
        md_test = {'name': 'functiontest', 'value': FUNC_TEST_NUM}
        md_azpub = {'name': 'cloud', 'value': 'azure-public'}
        md_azgov = {'name': 'cloud', 'value': 'azure-government'}

        md = [md_prod, md_type, md_test]

        ## Where is {id} in preview?
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_preview(id),
            'source': QnA_SOURCE,
            'questions': [ f"{word}is {id} in preview?" for word in ['','Where '] ],
            'metadata': md.copy()
        })

        ## ... in Azure Commercial?
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_preview_in(id, 'azure-public'),
            'source': QnA_SOURCE,
            'questions':
                [ f"{word}is {id} in preview in Azure Commercial?" for word in ['','Where '] ] +
                [ f"{word}is {id} in preview in Azure Public?" for word in ['','Where '] ],
            'metadata': md + [md_azpub]
        })

        ## ... in Azure Government?
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_preview_in(id, 'azure-government'),
            'source': QnA_SOURCE,
            'questions':
                [ f"{word}is {id} in preview in Azure Government?" for word in ['','Where '] ] +
                [ f"{word}is {id} in preview in MAG?" for word in ['','Where '] ]
            ,
            'metadata': md + [md_azgov]
        })

        # yapf: enable

    def __hydrate_expected_qna(self, id):

        # yapf: disable

        md_prod = {'name': 'product', 'value': id.replace('|', ' ').replace(':', ' ')}
        md_type = {'name': 'questionType', 'value': 'expected-question'}
        md_test = {'name': 'functiontest', 'value': FUNC_TEST_NUM}
        md_azpub = {'name': 'cloud', 'value': 'azure-public'}
        md_azgov = {'name': 'cloud', 'value': 'azure-government'}

        md = [md_prod, md_type, md_test]

        ## When is {id} expected to be available?
        self.__qna.append({
            'id': len(self.__qna),
            'answer': _b(id) + self.answer_where_expected_ga(id),
            'source': QnA_SOURCE,
            'questions': [f"When is {id} expected to be {word}" for word in ['available', 'ga', 'GA'] ],
            'metadata': md.copy()
        })

        ## ... in Azure Commercial?
        self.__qna.append({
            'id': len(self.__qna),
            'answer':  _b(id) + self.answer_where_expected_ga_in(id, 'azure-public'),
            'source': QnA_SOURCE,
            'questions':
                [f"When is {id} expected to be {word} in Azure Commercial" for word in ['available', 'ga', 'GA'] ] +
                [f"When is {id} expected to be {word} in Azure Public" for word in ['available', 'ga', 'GA'] ],
            'metadata': md + [md_azpub]
        })

        ## ... in Azure Government?
        self.__qna.append({
            'id': len(self.__qna),
            'answer':  _b(id) + self.answer_where_expected_ga_in(id, 'azure-government'),
            'source': QnA_SOURCE,
            'questions':
                [f"When is {id} expected to be {word} in Azure Government" for word in ['available', 'ga', 'GA'] ] +
                [f"When is {id} expected to be {word} in MAG" for word in ['available', 'ga', 'GA'] ],
            'metadata': md + [md_azgov]
        })

        # yapf: enable

    def __hydrate_scopes_qna(self, id):

        # yapf: disable

        md_prod = {'name': 'product', 'value': id.replace('|', ' ').replace(':', ' ')}
        md_type = {'name': 'questionType', 'value': 'scope-question'}
        md_test = {'name': 'functiontest', 'value': FUNC_TEST_NUM}
        md_azpub = {'name': 'cloud', 'value': 'azure-public'}
        md_azgov = {'name': 'cloud', 'value': 'azure-government'}

        md = [md_prod, md_type, md_test]

        ## answer 1
        id_all_scopes = len(self.__qna)
        self.__qna.append({
            'id': id_all_scopes,
            'answer': _b(id) + self.answer_which_scopes(id),
            'source': QnA_SOURCE,
            'questions': [
                f"Which audit scopes is {id} at?",
                f"Which scopes is {id} at?",
                f"Which impact levels is {id} at?"
            ],
            'metadata': md.copy()
        })

        ## answer 2
        id_azpub = len(self.__qna)
        self.__qna.append({
            'id': id_azpub,
            'answer': f"{_b(id)}{self.answer_which_scopes_in_cloud(id, 'azure-public')}",
            'source': QnA_SOURCE,
            'questions': [
                f"Which audit scopes is {id} at in Azure Commercial?",
                f"Which impact levels is {id} at in Azure Commercial?"
            ],
            'metadata': md + [md_azpub]
        })

        ## answer 3
        id_azgov = len(self.__qna)
        self.__qna.append({
            'id': id_azgov,
            'answer': f"{_b(id)}{self.answer_which_scopes_in_cloud(id, 'azure-government')}",
            'source': QnA_SOURCE,
            'questions': [
                f"Which audit scopes is {id} at in Azure Government?",
                f"Which impact levels is {id} at in Azure Government?",
                f"Which audit scopes is {id} at in MAG?",
                f"Which impact levels is {id} at in MAG?",
            ],
            'metadata': md + [md_azgov]
        })


        ## is at {each IL level} ? ------------------
        self.__helper_hydrate_is_scope(id,
            'IL2',
            ['IL2', 'IL 2', 'DoD CC SRG IL 2'],
            ['azure-public','azure-government'],
            md)

        self.__helper_hydrate_is_scope(id,
            'IL4',
            ['IL4', 'IL 4', 'DoD CC SRG IL 4'],
            ['azure-government'],
            md)

        self.__helper_hydrate_is_scope(id,
            'IL5',
            ['IL5', 'IL 5', 'DoD CC SRG IL 5 (Azure Gov)', 'DoD CC SRG IL 5 (Azure DoD)',
            'IL5 in Gov', 'IL5 in DOD', 'DoD CC SRG IL 5'],
            ['azure-government'],
            md)

        self.__helper_hydrate_is_scope(id,
            'IL6',
            ['IL6', 'IL 6', 'DoD CC SRG IL 6'],
            ['azure-government'],
            md)

        self.__helper_hydrate_is_scope(id,
            'FedRAMP Moderate',
            ['FedRAMP Moderate'],
            ['azure-public'],
            md)


        self.__helper_hydrate_is_scope(id,
            'FedRAMP High',
            ['FedRAMP High'],
            ['azure-public', 'azure-government'],
            md)

        return [id_all_scopes, id_azpub, id_azgov]

        # yapf: enable

    def __helper_hydrate_is_scope(self, id, scope, names, cloud_list, metadata_starter):

        # yapf: disable

        md_scope = {'name':'scope', 'value': scope }

        md_azpub = {'name': 'cloud', 'value': 'azure-public'}
        md_azgov = {'name': 'cloud', 'value': 'azure-government'}
        md_cloud = {
            'azure-public' : md_azpub,
            'azure-government': md_azgov
        }

        md_question_starter = []

        if len(cloud_list) > 1:
            self.__qna.append({
                'id': len(self.__qna),
                'answer': self.answer_is_at_scope(id, scope),
                'source': QnA_SOURCE,
                'questions': [ f"Is {id} at {il}?" for il in names ],
                'metadata': metadata_starter + [md_scope]
            })
        else:
            md_question_starter = [ f"Is {id} at {il}?" for il in names ]

        for cloud in cloud_list:
            md_questions = [ f"Is {id} at {il} in {self.__cloud_name(cloud)}?" for il in names ]

            if cloud == 'azure-government':
                md_questions = md_questions + [ f"Is {id} at {il} in MAG?" for il in names ]

            self.__qna.append({
                'id': len(self.__qna),
                'answer': self.answer_is_at_scope_in_cloud(id, scope, cloud),
                'source': QnA_SOURCE,
                'questions': md_question_starter + md_questions,
                'metadata': metadata_starter + [md_scope, md_cloud[cloud]]
            })

        # yapf: enable

    def __answer_what_services(self):
        return "I know about the following services:" + list_to_markdown(self.__az.services_list())

    def __answer_what_services_in_cloud(self, cloud):
        pass

    '''
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
    '''

    def answer_where_ga(self, id):
        return (
            self.answer_where_ga_in(id, 'azure-public') + '\n\n' + 'It' +
            self.answer_where_ga_in(id, 'azure-government')
        )

    def answer_where_ga_in(self, id, cloud):
        cloud_name = self.__cloud_name(cloud)
        regions = self.__az.getProductAvailableRegions(id, cloud)

        if "non-regional" in regions or "usgov-non-regional" in regions:
            return f" is GA in {cloud_name}. It is {_i('non-regional')} and not tied to a specific region."

        # return regions
        if len(regions) > 0:
            return " is GA in %s in: %s" % (cloud_name, list_to_markdown(regions))

        # it is not GA, check preview regions and expected release date

        ans = " is not currently GA in %s. " % (cloud_name)

        preview = self.answer_where_preview_in(id, cloud)
        preview = "However, it" + preview

        if "is not" not in preview:
            ans = ans + "\n\n" + preview

        expected = self.answer_where_expected_ga_in(id, cloud)
        expected = "It" + expected

        if "is not" not in expected:
            ans = ans + "\n\n" + expected

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
            " is ***In Preview*** in *both* Azure Commercial and Azure Government.\n\n" + "It" +
            az_pub + "\n\n" + "It" + az_gov
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

        return (az_pub + "\n\n" + "It" + az_gov)

    def answer_where_expected_ga_in(self, id, cloud):
        ans = ""
        cloud_name = self.__cloud_name(cloud)
        available = self.__az.isProductAvailable(id, cloud)
        expected_ga = self.__az.getProductRegionsGATargets(id, cloud)

        if available:
            regions_ga = list_to_markdown(self.__az.getProductAvailableRegions(id, cloud))
            ans = " is already GA in %s in %s" % (cloud_name, regions_ga)

            if (len(expected_ga) == 0):
                return ans

            ans = ans + "It"

        if (len(expected_ga) > 0):
            pretty_expected = self.__pretty_expected_list(expected_ga)
            return ans + " is currently targeted for GA in %s: %s" % (
                cloud_name, list_to_markdown(pretty_expected)
            )

        return " is not currently scheduled for GA in %s. " % cloud_name

    def answer_is_at_scope(self, id, scope):
        az_pub = self.answer_is_at_scope_in_cloud(id, scope, 'azure-public')
        az_gov = self.answer_is_at_scope_in_cloud(id, scope, 'azure-government')

        in_az_pub = "Yes" in az_pub
        in_az_gov = "Yes" in az_gov

        if in_az_gov and in_az_pub:
            return f"Yes. {_b(id)} is at {scope} in both {_i('Azure Commercial')} and {_i('Azure Government')}"
        elif in_az_pub:
            return az_pub
        elif in_az_gov:
            return az_gov

        return (
            f"No, it does not look like {_b(id)} is at {scope} in either {_i('Azure Commercial')} and {_i('Azure Government')}"
            + "\n\nIt" + self.answer_which_scopes_in_cloud(id, 'azure-public') + "\n\nIt" +
            self.answer_which_scopes_in_cloud(id, 'azure-government')
        )

    def answer_is_at_scope_in_cloud(self, id, scope, cloud):
        scopes = self.answer_which_scopes_in_cloud(id, cloud)

        if "il 2" in scope.lower() or "il2" in scope.lower(): scope_short = "IL 2"
        elif "il 4" in scope.lower() or "il4" in scope.lower(): scope_short = "IL 4"
        elif "il 5" in scope.lower() or "il5" in scope.lower(): scope_short = "IL 5"
        elif "il 6" in scope.lower() or "il6" in scope.lower(): scope_short = "IL 6"
        else: scope_short = scope

        if scope_short in scopes:
            il5_suffix = self.__helper_scope_il5_region_checker(scope_short, scopes)
            return f"Yes, {_b(id)} is at {scope_short} in {self.__cloud_name(cloud)}{il5_suffix}."
        else:
            return (
                f"No, {_b(id)} is not at {scope_short} in {self.__cloud_name(cloud)}" +
                f"\n\nIt{scopes}"
            )

    def __helper_scope_il5_region_checker(self, scope, scopes):

        if scope == "IL 5":
            gov = "DoD CC SRG IL 5 (Azure Gov)" in scopes
            dod = "DoD CC SRG IL 5 (Azure DoD)" in scopes

            if (gov and dod):
                return " in **both Gov and DoD regions**"
            elif gov:
                return ", but in **Gov regions only**"
            elif dod:
                return ", but in **DoD regions only**"

        return ""

    def answer_which_scopes(self, id):
        az_pub = self.answer_which_scopes_in_cloud(id, 'azure-public')
        az_gov = self.answer_which_scopes_in_cloud(id, 'azure-government')

        return az_pub + "\n\nIt" + az_gov

    def answer_which_scopes_in_cloud(self, id, cloud):
        cloud_name = self.__cloud_name(cloud)
        scopes = self.__az.getProductScopes(id, cloud)

        if len(scopes) > 0:
            return f" is in {cloud_name} at the following scopes {list_to_markdown(scopes)}"

        return f" does not have an audit scope or impact level info available yet for {cloud_name}."

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
        if (cloud == 'azure-public'): return _i("Azure Commercial")
        if (cloud == 'azure-government'): return _i("Azure Government")

        raise Exception("Unknown cloud", cloud)

    def __pretty_expected_list(self, in_list):
        return [i['region'] + " (" + i['ga-expected'] + ")" for i in in_list]

    def dump(self):
        return self.__az.product_list()

    ########################## --------------------------------------------------------------------------------------------------------
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
