import datetime

from django.test import TestCase
from django.test import Client
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose
        pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text='test question text', days=5):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question, choice_text='test_choice_text', votes_amount=0):
    """
    Create a choice with the given `choice_text` and `votes` for the given `question`
    """
    return Choice.objects.create(question=question, choice_text=choice_text, votes=votes_amount)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        create_choice(question1)
        question2 = create_question(question_text="Past question 2.", days=-5)
        create_choice(question2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [question2, question1],
        )

    def test_question_without_choices(self):
        """
        Questions without choices shouldn't display at index page
        """
        question_without_choices = create_question(question_text="Question without choices", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], [],
        )


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question", days=5)
        url = reverse('polls:detail', args=(future_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choice(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        create_choice(past_question)
        url = reverse('polls:detail', args=(past_question.pk,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_without_choice(self):
        """
        The detail view of a question without choice with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse('polls:detail', args=(past_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class QuestionResultViewTest(TestCase):
    def test_future_question(self):
        """
        The result view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future Question", days=5)
        create_choice(future_question)
        url = reverse('polls:results', args=(future_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question_with_choice(self):
        """
        The result view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past question", days=-5)
        create_choice(past_question)
        url = reverse('polls:results', args=(past_question.pk,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_without_choice(self):
        """
        The result of a question without choices with a pub_date in the past returns a 404 not found
        """
        past_question = create_question(question_text="Past question", days=-5)
        url = reverse('polls:results', args=(past_question.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class VoteTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.question = create_question()
        self.choice = create_choice(self.question)

    def test_vote_view_with_valid_choice_change_votes_counter(self):
        """
        The result of post form with valid choice is changing votes += 1
        """
        self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(Choice.objects.get(pk=self.choice.id).votes, 2)

    def test_vote_view_with_valid_choice_redirect_to_details(self):
        """
        The result of post form with valid choice is redirection to <int:pk>/results page
        """
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(response.url, reverse('polls:results', args=(self.question.id,)))

    def test_vote_view_with_invalid_choice(self):
        """
        The result of post form without selected choice is error message
        """
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You didn&#x27;t select a choice.")
