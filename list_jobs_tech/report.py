from sqlalchemy import desc

from .database import JobOffer, Technology, ManageDatabase


class Report:
    @property
    def session(self):
        return ManageDatabase.get_session()

    def report_should_learn(self):
        return (
            self.session.query(Technology)
            .filter(Technology.skill_level == 0)
            .order_by(desc(Technology.average_score))
            .limit(2).all()
        )

    def report_should_deepen(self):
        return (
            self.session.query(Technology)
            .filter(Technology.skill_level > 0)
            .order_by(desc(Technology.deepen_score))
            .limit(5).all()
        )

    def report_should_look(self):
        return (
            self.session
            .query(JobOffer)
            .order_by(desc(JobOffer.score))
            .limit(10).all()
        )

    def report(self):
        print('You should learn :')
        for tech in self.report_should_learn():
            print(f"    - {tech.name} : {tech.average_score}")
        print('You should deepen :')
        for tech in self.report_should_deepen():
            print(f"    - {tech.name} : {tech.deepen_score} {tech.skill_level}")
        print("You should look :")
        for offer in self.report_should_look():
            print(f"    - {offer.score} : ")
            print(f"{8*' '}{offer.url}")
