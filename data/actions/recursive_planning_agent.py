# recursive_planning_agent.py

from plugin_base import PluginBase
import pprint
from models import ActionTrace, ActionStatus
from datetime import datetime

class RecursivePlanningAgentPlugin(PluginBase):
    def __init__(self, context, debug=False):
        super().__init__(context, debug)
        self.register_action('recursive_planning_agent', self.recursive_planning_agent)

    def recursive_planning_agent(self):
        # Get parameters from DI layer
        max_depth = self.di_layer.get('max_depth', default=3)
        max_breadth = self.di_layer.get('max_breadth', default=5)

        # Get the initial concept
        concept = self.di_layer.get('concept')
        if not concept:
            concept = self.di_layer.get('problem')
            self.di_layer.set('concept', concept)

        # Begin exploration
        concept_hierarchy = self._explore_concepts(concept, current_depth=1, max_depth=max_depth, max_breadth=max_breadth)

        # Store the concept hierarchy in the DI layer
        self.di_layer.set('concept_hierarchy', concept_hierarchy)

        # Optionally, print or log the hierarchy
        pp = pprint.PrettyPrinter(indent=2)
        self.logger.debug('\nFinal Concept Hierarchy:')
        self.logger.debug(pp.pformat(concept_hierarchy))

        return concept_hierarchy

    def _explore_concepts(self, concept, current_depth, max_depth, max_breadth):
        # Create a new ActionTrace entry
        parent_trace_id = self.di_layer.get('current_trace_id')
        action_trace = ActionTrace(
            execution_id=self.execution_id,
            action_name='_explore_concepts',
            component=self.__class__.__name__,
            start_time=datetime.utcnow(),
            status=ActionStatus.STARTED,
            input_data={'concept': concept, 'current_depth': current_depth},
            parent_trace_id=parent_trace_id
        )
        self.db_session.add(action_trace)
        self.db_session.commit()

        # Use the trace_context to update current_trace_id
        with self.di_layer.trace_context(action_trace.trace_id):
            try:
                if current_depth > max_depth:
                    self.logger.debug(f"Maximum depth {max_depth} reached for concept: {concept}")
                    return None

                indent = '  ' * (current_depth - 1)
                self.logger.debug(f"{indent}Exploring at depth {current_depth}: {concept}")

                # Set the current concept
                self.di_layer.set('concept', concept)

                # Decide whether to explore this concept further
                should_explore = self.execute_action('should_explore_agent')
                if not should_explore:
                    self.logger.debug(f"{indent}Decided not to explore '{concept}' further.")
                    return None

                # Generate sub-concepts
                subconcepts = self.execute_action('list_subconcepts_agent')

                # Process the subconcepts
                if not subconcepts:
                    self.logger.debug(f"{indent}No further concepts found for '{concept}'.")
                    return None

                # Flatten the subconcepts and limit to breadth
                flattened_subconcepts = []
                for item_dict in subconcepts:
                    if isinstance(item_dict, dict):
                        for _, item_value in item_dict.items():
                            if isinstance(item_value, str):
                                flattened_subconcepts.append(item_value.strip())
                            else:
                                self.logger.warning(f"Expected a string, but got {type(item_value)}: {item_value}")
                    else:
                        self.logger.warning(f"Expected a dict, but got {type(item_dict)}: {item_dict}")
                if not flattened_subconcepts:
                    self.logger.debug(f"{indent}No valid subconcepts to explore for '{concept}'.")
                    return None

                # Limit to breadth
                flattened_subconcepts = flattened_subconcepts[:max_breadth]

                # Collect concepts and recurse
                concept_tree = {}
                for sub_concept in flattened_subconcepts:
                    self.logger.debug(f"{indent}- {sub_concept}")
                    sub_tree = self._explore_concepts(sub_concept, current_depth + 1, max_depth, max_breadth)
                    concept_tree[sub_concept] = sub_tree

                # Update ActionTrace
                action_trace.end_time = datetime.utcnow()
                action_trace.status = ActionStatus.COMPLETED
                action_trace.output_data = {'concept_tree': concept_tree}
                self.db_session.commit()
                return concept_tree

            except Exception as e:
                # Update ActionTrace on failure
                action_trace.end_time = datetime.utcnow()
                action_trace.status = ActionStatus.FAILED
                action_trace.output_data = {'error': str(e)}
                self.db_session.commit()
                self.logger.error(f"Error executing action '_explore_concepts': {e}")
                raise
