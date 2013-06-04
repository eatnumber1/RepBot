#!/usr/bin/python

from twisted.internet import reactor

def get_channel_arg(channel, args):
	if args and args[0].startswith(('#','&','+','!')):
		channel = args[0]
		args.pop(0)
	return channel

def Action(name, helpmsg):
	class ActionClass(object):
		__slots__=('name','helpmsg', 'cmd')
		def __init__(self, f):
			self.name = name
			self.helpmsg = helpmsg
			self.cmd = f
		def __call__(self, *args, **kwargs):
			return self.cmd(*args,**kwargs)
	return ActionClass

@Action("help", "List command help")
def Action_help(bot, user, args):
	if len(args):
		for arg in args:
			a = globals().get("Action_"+arg)
			if a: bot.msg(user, "{0}:\t{1}".format(a.name, a.helpmsg))
	else:
		bot.msg(user, "\n".join("{0}:\t{1}".format(a.name, a.helpmsg)
					for a in globals()
					if a.startswith("Action_")))

@Action("verify", "Confirm admin access")
def Action_verify(bot, user, args):
	bot.msg(user, "Authentication valid");

@Action("admin", "Adjust user admin access")
def Action_admin(bot, user, args):
	if len(args) < 2:
		bot.msg(user, "Admin change failed: too few arguments")
		return
	cmd = args[0]
	args = args[1:]
	if cmd == "add": bot.admins |= set(args)
	elif cmd in ("remove","rm"): bot.admins -= set(args)
	else: bot.msg(user, "Admin change failed: unknown action")

@Action("ignore", "Adjust ignore list")
def Action_ignore(bot, user, args):
	if len(args) < 2:
		bot.msg(user, "Ignore change failed: too few arguments")
		return
	cmd = args[0]
	args = args[1:]
	if cmd == "add": bot.ignorelist |= set(args)
	elif cmd in ("remove","rm"): bot.ignorelist -= set(args)
	elif cmd == "list": bot.msg(user, str(list(bot.ignorelist)))
	else: bot.msg(user, "Ignore change failed: unknown action") 

@Action("dump", "Dump database to a file")
def Action_dump(bot, user, args):
	bot.reps.dump()
	bot.log("Rep file dumped")

@Action("filter", "Remove unused entries")
def Action_filter(bot, user, args):
	bot.reps.filter()
	bot.log("Filtered zeroed entries")

@Action("clear", "Remove the given names from the system")
def Action_clear(bot, user, args):
	if len(args) == 1 and args[0] == "all":
		bot.reps.reps = {}
	else:
		for name in args:
			bot.reps.clear(name)

@Action("tell", "Tell a channel rep information for users")
def Action_clear(bot, user, args):
	user = get_channel_arg(user, args)
	for name in args:
		bot.msg(user, bot.reps.tell(name))

@Action("all", "Get all reputations")
def Action_all(bot, user, args):
	user = get_channel_arg(user, args)
	bot.msg(user, bot.reps.all())

@Action("limit", "Adjust limits")
def Action_limit(bot, user, args):
	if len(args) < 2:
		bot.msg(user, "Limit change failed: too few arguments")
		return
	cmd = args[0]
	args = args[1:]
	if cmd == "rep":
		if args: bot.replimit = int(args[0])
		else: bot.msg(user, "Rep limit: {0}".format(bot.replimit))
	elif cmd == "time":
		if args: bot.timelimit = int(args[0])
		else: bot.msg(user, "Time limit: {0}".format(bot.timelimit))
	else:
		bot.msg(user, "Limit change failed: unknown limit")

@Action("set", "Manually set a user's rep value")
def Action_set(bot, user, args):
	if len(args) != 1: bot.msg(user, "Set failed: incorrect number of arguments")
	bot.reps.set(args[0], int(args[1]))

@Action("allow", "Clear rep timeout restrictions for all given users")
def Action_set(bot, user, args):
	for name in args: bot.users[name]=[]

@Action("auto", "Adjust autorespond mode")
def Action_autorespond(bot, user, args):
	if args: bot.autorespond = (args[0].lower()=="on")
	bot.msg(user, "Autorespond is "+("on" if bot.autorespond else "off"))

@Action("private", "Adjust private message restriction mode")
def Action_autorespond(bot, user, args):
	if args: bot.privonly = (args[0].lower()=="on")
	bot.msg(user, "Private messaging restriction is "+("on" if bot.privonly else "off"))

@Action("apply", "Apply the Python dictionary provided to the rep database")
def Action_apply(bot, user, args):
	bot.reps.update(eval("".join(args)))

@Action("term", "Safely terminate RepBot")
def Action_term(bot, user, args):
	bot.reps.dump()
	bot.quit(" ".join(args))
	reactor.stop()

@Action("join", "Join a channel")
def Action_join(bot, user, args):
	for chan in args:
		bot.join(chan)

@Action("part", "Leave a channel")
def Action_part(bot, user, args):
	for chan in args:
		bot.leave(chan)

@Action("report", "Generate a report")
def Action_report(bot, user, args):
	if len(args) > 1: bot.msg(user, "Report failed: Too many arguments")
	bot.msg(args[0] if args else user, bot.reps.report())

def admin(bot, user, msg):
	if not msg.strip(): return
	command = msg.split()[0].lower()
	args = msg.split()[1:]
	action = globals().get("Action_"+command)
	if action:
		action(bot, user, args)
	else: 
		print "Invalid command {0}".format(command)
