import dspy

from dspy_profiles import with_profile


class QA(dspy.Signature):
    """Given a question return the answer"""

    question: str = dspy.InputField()
    answer: str = dspy.OutputField()


@with_profile("default")
class MyModule(dspy.Module):
    def __init__(self, callbacks=None):
        super().__init__(callbacks)
        self.pred = dspy.Predict(QA)

    def forward(self, question):
        return self.pred(question="What is DSPy?").answer


def main():
    my_mod = MyModule()
    print(f"{my_mod('What is DSPy?')}")


if __name__ == "__main__":
    main()
