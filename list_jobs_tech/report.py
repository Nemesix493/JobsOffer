from sqlalchemy import desc, func
from jinja2 import Environment, FileSystemLoader

from .database import JobOffer, Technology, ManageDatabase
from .settings import TEMPLATES_DIR


class Report:
    @property
    def session(self):
        return ManageDatabase.get_session()

    @property
    def report_should_learn(self):
        if not hasattr(self, "_should_should_learn_deepen"):
            setattr(
                self,
                "_should_learn",
                (
                    self.session.query(Technology)
                    .filter(Technology.skill_level == 0)
                    .order_by(desc(Technology.average_score))
                    .limit(2).all()
                )
            )
        return getattr(self, "_should_learn")

    @property
    def report_should_deepen(self):
        if not hasattr(self, "_should_deepen"):
            setattr(
                self,
                "_should_deepen",
                (
                    self.session.query(Technology)
                    .filter(Technology.skill_level > 0)
                    .order_by(desc(Technology.deepen_score))
                    .limit(5).all()
                )
            )
        return getattr(self, "_should_deepen")

    def get_should_look(self):
        max_time_adjusted = self.session.query(
            func.max(JobOffer.time_adjusted)
        ).scalar_subquery()
        reported_offer = (
            self.session.query(
                JobOffer,
                (
                    (3 * JobOffer.score + (10 * JobOffer.time_adjusted / max_time_adjusted)) / 5
                ).label('time_adjusted_score')
            ).filter(JobOffer.score >= 3)
            .filter(JobOffer.reported is not True)
            .order_by(desc('time_adjusted_score'))
            .limit(5).all()
        )
        should_look = []
        for job_offer, time_adjusted_score in reported_offer:
            job_offer.reported = True
            job_offer.set_time_adjusted_score = time_adjusted_score
            should_look.append(job_offer)
            self.session.add(job_offer)
        self.session.commit()
        return should_look

    @property
    def report_should_look(self):
        if not hasattr(self, "_should_look"):
            setattr(
                self,
                "_should_look",
                self.get_should_look()
            )
        return getattr(self, "_should_look")

    def print_report(self):
        print('You should learn :')
        for tech in self.report_should_learn:
            print(f"    - {tech.name} : {tech.average_score}")
        print('You should deepen :')
        for tech in self.report_should_deepen:
            print(f"    - {tech.name} : {tech.deepen_score} {tech.skill_level}")
        print("You should look :")
        for offer in self.report_should_look:
            print(f"    - {offer.score} : ")
            if offer.time_adjusted_score:
                print(f"{8*' '}{offer.time_adjusted_score}")
            print(f"{8*' '}{offer.url}")

    def html(self):
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("report.html")
        result = template.render(report=self)
        env.cache.clear()
        return result
