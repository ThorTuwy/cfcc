import Codeforces.CodeforcesRequester
from utils.program_configs import CodeforcesConfig

cf_requester = Codeforces.CodeforcesRequester.CodeforcesRequester(CodeforcesConfig())

cf_requester.submit_problem("2200","A", "pan-con-jamon")