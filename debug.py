import sys
from pathlib import Path

MAIN_PATH = Path(sys.argv[0]).resolve().parent



def render_behavior_tree(extension: str) -> None:
    """
    Display behavior tree
    """
    from py_trees import display
    from companions.Sebastian.behavior_tree import create_tree

    class Companion():
        pass

    tree = create_tree(Companion())

    if extension == 'dot':
        display.render_dot_tree(
            root=tree,
            target_directory=MAIN_PATH
        )
    elif extension == 'html':
        title = "Sebastian Behavior"

        with open(MAIN_PATH / 'behavior.html', 'w') as f:
            f.write('<html>')
            f.write(f'<head><title>{title}</title></head>')
            f.write('<<body>')
            f.write(display.xhtml_tree(tree))
            f.write("</body>")
            f.write("</html>")
        
        display.dot_tree(root=tree)



if __name__ == '__main__':
    render_behavior_tree('html')