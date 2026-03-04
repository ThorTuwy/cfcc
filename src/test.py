from Codeforces.CodeforcesRequester import CodeforcesRequester
from utils.program_configs import CodeforcesConfig

cf_req=CodeforcesRequester(CodeforcesConfig())

req=cf_req.get_problem_data_by_id("2200","3966075")
print(req.status_code)
print(req.text)