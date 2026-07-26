Essentialy the project is a naked OS kernel plus a few examle applications that are hard to navigate for non-tech people.

Intention and motivation:
Since fundamentally I believe the architecture, philosophy and paradigm are world-class - all the effort is aimed to show this 'class' to the world.

Big picture solution:
For adoption - we need users. Users need simplicity and use case.

Team engineers - devops
The project installation is non trivial. (asking claude to install the project). Everything was developed and tested on linux. Some people have working instances on MacOS, windows completely missed.
Brainstorm the scope with Team world adoption (see below) and ensure smooth
* instalation
* setup.
* usage of agreed scope
 The result is a deliverable packaged, user friendly instance.
Basically your job is to turn a linux kernel into sth. like ubuntu.

Team engineers - infrastructure extension
Architecture allows adding many features/plugins and components. Some of suggested features are scattered as issues across different repositories in the organization. Take those as inspiration, reason   which could lead to quickest gains in adoption. Scope to what is agreed with Team world adoption (see below)
20% of effort %80 of result.



Team world adoption
Your job is to ensure that Diotima will find it's first big user by finding a usecase and following through negotiation.
Example: Charles university - medical faculty - spaced repetition generator of cards for students for select memory intense subjects.
Example: big government institution that needs a bot to train employees during onboarding
Example: finding a company that would like to implement examples above for profit.
Participate in brainstorming phase of first two teams. Come up with a real use case that can be onboarded into some organization.


Team engineers - guardrail architecture 
Assume user is not technical - guardrails shall protect the setup from their own selves. Imagine a user telling claude: "I have google keep, can you sync my notes with this setup?" thinking that it's a trivial request, while infrastructure not having google mcp at a time - might turn their local repo into a mess. (Semantic & deterministic guardrails)
Might require a separate component and research on best existing practices. (Dummy implementation - on user prompt hook cheap model filter)


Team enginers - optimization
Project was constructed very quicly with one sole  focus on architecture (macro level platform). Optimization, token efficiency and guardrails/edge cases were forseen, yet ruthlessly sacrificed.
Many parts of the project unnecessary rely on LLM orchestration where the task could have been solved by deterministic hook invocations or executables.
Establish communication channel with other engineer teams to prevent their poor optimization in the root.
