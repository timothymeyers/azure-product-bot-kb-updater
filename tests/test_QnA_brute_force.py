import pytest
from azure_data_scraper.az_product_info import AzProductInfo
from com.QnA_brute_force import (QnABruteForce, list_to_markdown)

# "Constaints"


# "Fixtures"
@pytest.fixture(scope="session")
def qna():
    return QnABruteForce(AzProductInfo(None, None, 'tests/tests.json'))


#Tests


def test_version():
    assert True


def test_list_to_markdown():
    assert list_to_markdown() == ""
    assert list_to_markdown([]) == ""
    assert list_to_markdown(['apples']) == "apples."
    assert list_to_markdown(['apples', 'bananas']) == "\\n * apples\\n * bananas\\n\\n"
    assert list_to_markdown(['apples', 'bananas', 'oranges',
                             'grapes']) == "\\n * apples, bananas, oranges, grapes \\n\\n"

def test_is_initialized(qna):
    assert True

@pytest.mark.parametrize("prod", [('Full Service')])
def test_answer_where_ga_in(qna, prod):
    ans = qna.answer_where_ga_in(prod, 'azure-public')
    assert "is GA" in ans
    assert "Azure Commercial" in ans
    assert "gcc-ga-reg-1" in ans
    assert "gcc-ga-reg-2" in ans

    ans = qna.answer_where_ga_in(prod, 'azure-government')
    assert "is GA" in ans
    assert "Azure Government" in ans
    assert "mag-ga-reg-1" in ans
    assert "mag-ga-reg-2" in ans


@pytest.mark.parametrize("prod, answer", [('Full Service', 'is GA'), ('Not GA Service', 'is not currently GA')])
def test_answer_where_ga_BOTH(qna, prod, answer):
    ans = qna.answer_where_ga(prod)
    assert answer in ans


@pytest.mark.parametrize("prod", [('Full Service')])
def test_answer_where_preview_in(qna, prod):
    ans = qna.answer_where_preview_in(prod, 'azure-public')
    assert "is ***In Preview" in ans
    assert "Azure Commercial" in ans
    assert "gcc-prev-reg-1" in ans

    ans = qna.answer_where_preview_in(prod, 'azure-government')
    assert "is ***In Preview" in ans
    assert "Azure Government" in ans
    assert "mag-prev-reg-1" in ans

@pytest.mark.parametrize("prod", [('Full Service')])
def test_answer_where_preview_BOTH (qna, prod):
    ans = qna.answer_where_preview (prod)
    assert "is ***In Preview" in ans
    assert "*both*" in ans

@pytest.mark.parametrize("prod", [('Full Service')])
def test_answer_where_expected_ga_in_IS_GA_TOO(qna, prod):
    ans = qna.answer_where_expected_ga_in(prod, 'azure-public')
    assert "is already GA" in ans
    assert "gcc-ga-reg-1" in ans
    assert "is currently targeted for GA" in ans
    assert "Azure Commercial" in ans
    assert "gcc-prev-reg-1 (Q2 2021)" in ans

    ans = qna.answer_where_expected_ga_in(prod, 'azure-government')
    assert "is already GA" in ans
    assert "mag-ga-reg-1" in ans
    assert "is currently targeted for GA" in ans
    assert "Azure Government" in ans
    assert "mag-prev-reg-1 (Q2 2021)" in ans

## WHY IS THIS BREAKING?

@pytest.mark.parametrize("prod", [('Not GA Service')])
def test_answer_where_expected_ga_in_IS_NOT_GA(qna, prod):
    ans = qna.answer_where_expected_ga_in(prod, 'azure-public')
    assert "is already GA" not in ans
    assert "is currently targeted for GA" in ans
    assert "Azure Commercial" in ans
    assert "gcc-prev-reg-1 (Q2 2021)" in ans

    ans = qna.answer_where_expected_ga_in(prod, 'azure-government')
    assert "is already GA" not in ans
    assert "is currently targeted for GA" in ans
    assert "Azure Government" in ans
    assert "mag-prev-reg-1 (Q2 2021)" in ans


'''
@pytest.mark.parametrize("prod, cloud, region", [
    ("Azure Blockchain Service", 'azure-public', "us-west-2"),
])
def test_answer_where_ga_in_IS_NOT_GA_BUT_PREVIEW(qna, prod, cloud, region):
    result = qna.answer_where_ga_in(prod, cloud)
    assert "is not currently GA in" in result
    assert "However, it is ***In Preview***" in result
    assert region in result
'''