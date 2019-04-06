#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2019)

Description: A set of classes for generating an assignment database.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import engine as SQLAlchemyEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table

Base = declarative_base()


class Sample(Base):
    """A table of samples representing genomes and metagenomes for which genome properties has been run on."""

    __tablename__ = 'samples'

    name = Column(String, primary_key=True)

    property_assignments = relationship('PropertyAssignment', back_populates='sample')

    def __repr__(self):
        return "<Sample(name='{}')>".format(self.name)


class PropertyAssignment(Base):
    """An assignment for a genome property (YES, NO, or PARTIAL)."""

    __tablename__ = 'property_assignments'

    assignment_identifier = Column(Integer, primary_key=True, autoincrement=True)
    property_number = Column(Integer)
    numeric_assignment = Column(Integer)  # 0 = YES, 1 = PARTIAL, 2 = NO
    sample_name = Column(String, ForeignKey('samples.name'))

    sample = relationship('Sample', back_populates='property_assignments')
    step_assignments = relationship('StepAssignment', back_populates='property_assignment')

    @property
    def assignment(self):
        """
        Takes assignments stored as integers and returns their word equivalent.
        :return: The assignment as a word.
        """
        assignment_type = self.numeric_assignment
        if assignment_type == 0:
            assignment = 'YES'
        elif assignment_type == 1:
            assignment = 'PARTIAL'
        elif assignment_type == 2:
            assignment = 'NO'
        else:
            assignment = 'unknown'

        return assignment

    @property
    def identifier(self):
        """
        Converts the properties number into its full property identifier.
        :return: The property identifier.
        """
        existing_property_number = self.property_number
        if existing_property_number:
            return 'GenProp{0:04d}'.format(existing_property_number)
        else:
            return 'unknown'

    @identifier.setter
    def identifier(self, value):
        """
        Converts the property identifier into an integer property number.
        :param value:
        """
        self.property_number = int(value.lower().split('prop')[1])

    @assignment.setter
    def assignment(self, value):
        """
        Takes word assignments stores them as integers
        :param value: The property assignment as YES, NO, or PARTIAL
        """
        if value == 'YES':
            self.numeric_assignment = 0
        elif value == 'PARTIAL':
            self.numeric_assignment = 1
        elif value == 'NO':
            self.numeric_assignment = 2
        else:
            self.numeric_assignment = 3

    def __repr__(self):
        sample = self.sample
        if sample:
            name = self.sample.name
        else:
            name = 'unknown'

        return "<PropertyAssignment(sample='{}', name='{}', assignment='{}')>".format(
            name,
            self.identifier,
            self.assignment)


# A joining table to handle the many to many relationship between steps and InterProScan matches.
step_match_association_table = Table('step_interpro_identifiers', Base.metadata,
                                     Column('step_assignment_identifier', Integer,
                                            ForeignKey('step_assignments.step_assignment_identifier')),
                                     Column('interproscan_match_identifier', Integer,
                                            ForeignKey('interproscan_matches.interproscan_match_identifier')))


class StepAssignment(Base):
    """An assignment for a genome property step. If present then it is assumed the step is present (e.g. YES)."""

    __tablename__ = 'step_assignments'

    step_assignment_identifier = Column(Integer, primary_key=True, autoincrement=True)
    property_number = Column(Integer, ForeignKey('property_assignments.property_number'))
    number = Column(Integer)

    property_assignment = relationship('PropertyAssignment', back_populates='step_assignments')
    interproscan_matches = relationship('InterProScanMatch', secondary=step_match_association_table,
                                        back_populates='step_assignments')
    assignment = 'YES'

    def __repr__(self):
        property_assignment = self.property_assignment
        if property_assignment:
            property_identifier = property_assignment.identifier
        else:
            property_identifier = 'unknown'

        return "<StepAssignment(Property='{}', number='{}', assignment={}')>".format(
            property_identifier, self.number, self.assignment)


class InterProScanMatch(Base):
    """Contains information about an InterProScan match supporting a step."""

    __tablename__ = 'interproscan_matches'

    interproscan_match_identifier = Column(Integer, primary_key=True, autoincrement=True)
    sequence_identifier = Column(String, ForeignKey('sequence.identifier'))
    interpro_signature = Column(String)
    expected_value = Column(Float)

    step_assignments = relationship('StepAssignment', secondary=step_match_association_table,
                                    back_populates='interproscan_matches')
    sequence = relationship('Sequence', back_populates='matches')

    def __repr__(self):
        sequence = self.sequence
        if sequence:
            sequence_identifier = sequence.sequence
        else:
            sequence_identifier = 'unknown'

        return "<InterProScanMatch(sequence_identifier='{0:s}', signature='{1:s}', assignment='{2:1.3e}')>".format(
            sequence_identifier,
            self.interpro_signature if self.interpro_signature else 'unknown',
            self.expected_value if self.expected_value else 1337)


class Sequence(Base):
    """Contains information about protein sequence."""

    __tablename__ = 'sequence'

    identifier = Column(String, primary_key=True)
    sequence = Column(String)

    matches = relationship('InterProScanMatch', back_populates='sequence')

    def __repr__(self):
        return "<Sequence(identifier='{}')>".format(self.identifier)


def write_assignment_results_to_database(results, engine: SQLAlchemyEngine):
    """
    Write the assignments to a database.
    :param results: A results object for Genome Properties.
    :param engine: An SQLAlchemy engine.
    """

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    current_session = sessionmaker(bind=engine)()
    for sample_name in results.sample_names:
        sample = Sample(name=sample_name)

        sample_step_assignments = []
        sample_property_assignments = []
        for property_identifier in results.properties:
            property_result = results.get_property_result(property_identifier,
                                                          sample=sample.name)

            property_assignment = PropertyAssignment(sample=sample)
            property_assignment.identifier = property_identifier
            property_assignment.assignment = property_result

            current_steps_assignments = []
            for step_number in results.get_step_numbers_for_property(property_identifier):
                step_result = results.get_step_result(property_identifier, step_number, sample=sample.name)

                if step_result == 'YES':
                    current_steps_assignments.append(StepAssignment(number=step_number,
                                                                    property_assignment=property_assignment))
                else:
                    continue  # Skip steps which are not 'YES' to save space.

            property_assignment.step_assignments = current_steps_assignments
            sample_step_assignments.extend(current_steps_assignments)
            sample_property_assignments.append(property_assignment)

        current_session.add_all([sample, *sample_property_assignments, *sample_step_assignments])
    current_session.commit()
    current_session.close()
