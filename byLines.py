#!/usr/bin/env python3
# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
from local_pip.colorama import init as coloramaInit, deinit as coloramaResetAll, Fore as txtColor , Back as txtColorBack, Style as txtStyle
import utils.utility_belt as uBelt
import utils.utility_git as uGit
from utils.utility_config import BaseConfigger
from sys import argv as sys_argv, version as sys_version, exit as sys_exit
from os import linesep as os_linesep
### Python 2/3
try:
  from typing import List, Set, Dict, Tuple, Text, Optional
except:
  pass
#######################

GITHUB_REPO_SRC = 'https://github.com/bleuf1sh/git-byLines'

COMMAND_COMMIT = 'commit'
COMMAND_DIRECT = 'direct'

def main(command):
  # type: (str) -> None
  coloramaInit()

  repo_hidden_configger = LocalRepoConfigger()
  repo_hidden_configger.loadJsonToConfigClass()
  if command is COMMAND_COMMIT and repo_hidden_configger.config_class.enabled is False:
    uBelt.log('git-byLines is disabled per RepoHiddenConfigger', isVerbose=True)
    exit(0)

  last_commit_hash = uGit.getGitCommitHash()
  # Run this all the time after each command trigger (used to be only after a recent commit)
  if True or (uBelt.getCurrentTimeEpochMs() - uGit.getGitCommitEpochMs(last_commit_hash)) >= 10000:
    triggerByLineWorkFlow(repo_hidden_configger, last_commit_hash)


def triggerByLineWorkFlow(repo_hidden_configger, commit_hash):
  # type: (LocalRepoConfigger, str) -> None
  uBelt.log('triggerByLineWorkFlow() ' + commit_hash, isVerbose=True)

  up_fish = '´¯`·.´¯`·.¸¸.·´¯`·.¸¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·><(((º>'
  dn_fish = '¸.·´¯`·.¸¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.><(((º>'
  sm_fish = '´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.·´¯`·.¸.><(((º>'

  cliPrint('')
  cliPrint('last commit:' + commit_hash)
  cliPrint(reset_colors() + '', 0)
  cliPrint(up_fish, 0)
  cliPrint("git-byLines makes it easy to add byLines to the most recent local commit", 0)
  cliPrint(dn_fish, 0)
  
  repo_visible_configger = RepoConfigger()
  repo_visible_configger.loadJsonToConfigClass()

  selected_bylines = [] # type: List[str]
  
  # Auto select the last commited byLines that we still have on file
  for recent_byline in repo_hidden_configger.config_class.lastByLines:
    if recent_byline in repo_visible_configger.config_class.byLines:
      selected_bylines.append(recent_byline)

  # Begin the Looping Interactive UI Prompts
  isFlowActive = True
  bylines = sorted(repo_visible_configger.config_class.byLines)
  while(isFlowActive):
    select_byline_prompt = ''
    if len(bylines) > 0:
      select_byline_prompt = 'Select by number or '
      cliPrint('')
      cliPrint('Enter the number to select a byLine:')
      abc123_list = list(range(1,len(bylines) + 1))
      for byline in bylines:
        if byline in selected_bylines:
          cliPrint(reset_colors() + txtColor.LIGHTYELLOW_EX + txtStyle.BRIGHT + '  ✔' + ' (' + str(abc123_list.pop(0)) + ') ' + byline)
        else:
          cliPrint(reset_colors() + txtColor.LIGHTYELLOW_EX + txtStyle.NORMAL + '   ' + ' (' + str(abc123_list.pop(0)) + ') ' + byline)
    
    cliPrint(reset_colors())
    cliPrint(reset_colors() + select_byline_prompt + 'Type a new byLine like ' + txtStyle.BRIGHT + 'Your Name <git-email@github.com>')
    cliPrint(reset_colors() + txtStyle.DIM + txtColor.BLACK + ':q Quit  :x Disable byLines  :a Ammend commit')
    cliPrint('')
    selected_input = uBelt.getInput(reset_colors() + '-> ').strip()
    if '' == selected_input:
      continue 
    if selected_input.lower() in ['x', ':x']:
      repo_hidden_configger.config_class.enabled = False
      repo_hidden_configger.saveConfigClassToJson()
      exitGracefully(0)
    if selected_input.lower() in ['q', ':q']:
      exitGracefully(0)
    if selected_input.lower() in ['a', ':a']:
      isFlowActive = False
    elif selected_input.isdigit():
      tag_index = selected_input.strip()
      try:
        byline = bylines[int(tag_index) - 1]
        if byline in selected_bylines:
          selected_bylines.remove(byline)
        else:
          selected_bylines.append(byline)
      except IndexError:
        show_warning('byLine selection unknown, please try again or exit')
    else:
      bylines.append(selected_input)
      bylines = sorted(bylines)
      selected_bylines.append(selected_input)
    
    cliPrint(sm_fish, 0)
    cliPrint('')
  
  # Update config with any newly added byLines
  for byline in bylines:
    if byline not in repo_visible_configger.config_class.byLines:
      repo_visible_configger.config_class.byLines.append(byline)

  repo_visible_configger.saveConfigClassToJson()
  did_ammend = addByLineToCommit(commit_hash, selected_bylines)
  if did_ammend is True:
    repo_hidden_configger.config_class.lastByLines = selected_bylines
    repo_hidden_configger.saveConfigClassToJson()


def addByLineToCommit(commit_hash, bylines_to_add):
  # type: (str, List[str]) -> bool
  uBelt.log('addByLineToCommit() ' + commit_hash + ': ' + str(bylines_to_add), isVerbose=True)
  if len(bylines_to_add) < 1:
    show_warning('No byLines selected to ammend to commit')
    return False
  
  ammended_commit_message = createAmmendedCommitMessage(commit_hash, bylines_to_add)
  cliPrint(reset_colors())
  cliPrint('Commit message after ammendement:')
  for line in ammended_commit_message.splitlines():
    cliPrint(reset_colors() + txtColor.LIGHTYELLOW_EX + line)

  cliPrint(reset_colors())
  selected_input = uBelt.getInput('Confirm the ammended commit message above? [y/N]: ')
  if selected_input.lower().startswith('n'):
    show_warning('Ammend aborted')
    return False

  # Ammend the commit
  uGit.ammendCommitMessage(ammended_commit_message)
  cliPrint('... DONE')
  return True

def createAmmendedCommitMessage(commit_hash, bylines_to_add):
  # type: (str, List[str]) -> str
  commit_message = uGit.getGitCommitMessage(commit_hash)
  new_line_character = getNewLineCharacter(commit_message)

  commit_message = commit_message + new_line_character

  # Attempt to detect if Author or Co
  if len(bylines_to_add) > 1 or commit_message.lower().find('authored-by: ') > 1:
    byline_prefix = 'Co-authored-by: '
  else:
    byline_prefix = 'Authored-by: '

  # Add the byLines to the message
  for byline in bylines_to_add:
    prefix_with_tag = byline_prefix + byline
    if commit_message.find(byline) == -1:
      commit_message = commit_message + new_line_character + prefix_with_tag
  
  return commit_message

def exitGracefully(code=0):
  print(txtStyle.RESET_ALL)
  coloramaResetAll()
  sys_exit(code)

def cliPrint(text, left_margin_amount=1):
  # type: (str, int) -> None
  encoded_padding_diff = len(text) - len(uBelt.ansi_strip(text))
  print(''.ljust(left_margin_amount) + text.ljust(84 + encoded_padding_diff - left_margin_amount))

def reset_colors():
  return txtStyle.NORMAL + txtColorBack.LIGHTBLACK_EX + txtColor.LIGHTWHITE_EX

def show_warning(txt):
  # type: (str) -> None
  uBelt.log(reset_colors() + txtColor.LIGHTRED_EX + '!!! ' + txt + ' !!!' + reset_colors())

def getNewLineCharacter(txt):
  # type: (str) -> str
  # Attempt to detect existing newline char
  if txt.find('\r\n'):
    new_line_character = '\r\n'
  elif txt.find('\n'):
    new_line_character = '\n'
  else:
    new_line_character = os_linesep
  
  return new_line_character


class LocalRepoConfigClass(object):
  def __init__(self):
    self.enabled = True # type: bool
    self.lastByLines = [] # type: List[str]
    self.repoSrc = GITHUB_REPO_SRC # type: str

  def __str__(self):
    return str(vars(self))

class LocalRepoConfigger(BaseConfigger) :
  def __init__(self):
    self.json_file_name = '.config.byLines.local.json' # type: str
    self.file_path_segments = [ uGit.getGitTopLevelDir(), '.git', self.json_file_name ] # type: List[str]
    self.config_class = LocalRepoConfigClass() # type: LocalRepoConfigClass


class RepoConfigClass(object):
  def __init__(self):
    self.byLines = [] # type: List[str]
    self.repoSrc = GITHUB_REPO_SRC # type: str

  def __str__(self):
    return str(vars(self))

class RepoConfigger(BaseConfigger) :
  def __init__(self):
    self.json_file_name = '.config.byLines.json' # type: str
    self.file_path_segments = [ uGit.getGitTopLevelDir(), self.json_file_name ] # type: List[str]
    self.config_class = RepoConfigClass() # type: RepoConfigClass



if __name__ == "__main__":
  uBelt.log('Python Version:' + sys_version, isVerbose=True)
  args = sys_argv
  uBelt.log('ARGS:' + str(args), isVerbose=True)
  
  if len(args) >= 2:
    switch_arg = args[1].lower().strip()
    uBelt.log('SwitchArg:' + switch_arg, isVerbose=True)

    if 'commit' == switch_arg:
      main(COMMAND_COMMIT)
  
  else:
    main(COMMAND_DIRECT)




