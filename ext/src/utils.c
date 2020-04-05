#include <time.h>
#include <stdlib.h>
#include <math.h>

#include "utils.h"

#define ENDPOINT 86400

/**
 * TESTED
 * interpolice
 */
long double interpolice(long double x, long double*f , long double*y, int num)
{
	long double res = 0.0;
	long double li = 1.0;
	for (int i = 0; i < num; i++)
	{
		if (!((-12 < (y[i] - x)) && ((y[i] - x) < 12)))
		{
			continue;
		}
		li = 1.0;
		for (int j = 0; j < num; j++)
		{
			if (!((-12 < (y[j] - x)) && ((y[j] - x) < 12)))
			{
				continue;
			}
			if (y[i] != y[j])
			{
				li *= ((x - y[j]) / (y[i] - y[j]));
			}
		}
		res += li * f[i];
	}
	return res;
}


/**
 * function to point value in each moment of time
 */
long double spread(weight_random_t* this,int x) {
	if ((this->x0 < x ) && ( x < this->x1))
	{
		return this->a * (x * x) + this->b * x + this->c;
	}
	else if (this->x0 > x) 
	{
		return (this->d / ((x+ENDPOINT) + this->k));
	}
	else
	{
		return (this->d / (x + this->k));
	}
}

/**
 * Constructor
 * params:
 *   p0 = [ x0 , x1 , y1 , y2]
 *   p1 = [ a, b, c]
 *   p2 = [ d, k ]
 */
weight_random_t* weight_random_create(long double* p0 ,long double* p1 ,long double* p2)
{
	if ((!p0) || (!p1) || (!p2))
	{
		return NULL;
	}
	weight_random_t * wr = (weight_random_t*)calloc(sizeof(weight_random_t),1);
	wr->x0 = p0[0];
	wr->x1 = p0[1];
	wr->y1 = p0[2];
	wr->y2 = p0[3];
	wr->a = p1[0];
	wr->b = p1[1];
	wr->c = p1[2];
	wr->d = p2[0];
	wr->k = p2[1];
	
	long double max = 0.0;
	wr->weights = (long double*)calloc(ENDPOINT,sizeof(long double));
	for (int i = 0; i < ENDPOINT; i++)
	{
		wr->weights[i] = spread(wr,i);
		max += wr->weights[i];
	}
	for (int i = 0; i < ENDPOINT; i++)
	{
		wr->weights[i] = wr->weights[i] / max;
	}
	return wr;
}

/**
 * return random value according to weights
 */
int weight_random_rand(weight_random_t* this, long double point)
{
	if (!this)
	{
		return 0;
	}
	int i=0;
	while ((i < ENDPOINT)&&(point > 0))
	{
		point -= this->weights[i];
		i++;
	}
	return (i-1);
}

/**
 * predict how many objs will be in 24 hours
 */
int weight_random_will_be(weight_random_t* this, int count_now, int now)
{
	if (!this)
	{
		return 0.0;
	}
	long double val = 0.0;
	for (int i = 0; i < ENDPOINT; i++)
	{
		val += this->weights[i];
	}
	return (int)(((long double)count_now) / val);
}

/**
 * destructure
 */
void weight_random_destruct(weight_random_t* this)
{
	if (!this)
	{
		return;
	}
	free(this->weights);
	free(this);
}
