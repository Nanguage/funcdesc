<div align="center">
  <h1> funcdesc </h1>

  <p> Establish a general function description protocol, which can realize a comprehensive description of the input, output and side effects of an target function through an Python object. Provide a unified abstraction for parameter checking, interface generation and other functions in applications such as oneFace. </p>

  <p>
    <a href="https://github.com/Nanguage/funcdesc/actions/workflows/build_and_test.yml">
        <img src="https://github.com/Nanguage/funcdesc/actions/workflows/build_and_test.yml/badge.svg" alt="Build Status">
    </a>
    <a href="https://app.codecov.io/gh/Nanguage/funcdesc">
        <img src="https://codecov.io/gh/Nanguage/funcdesc/branch/master/graph/badge.svg" alt="codecov">
    </a>
    <a href="https://pypi.org/project/funcdesc/">
      <img src="https://img.shields.io/pypi/v/funcdesc.svg" alt="Install with PyPi" />
    </a>
    <a href="https://github.com/Nanguage/funcdesc/blob/master/LICENSE">
      <img src="https://img.shields.io/github/license/Nanguage/funcdesc" alt="MIT license" />
    </a>
  </p>
</div>


## Features

* Parse function to get a description object.
* Mark function's inputs and outputs
* Mark function's side effects
* Generate checker(guard) for function
  + Check inputs and outputs's type.
  + Check inputs and outputs's range.
  + **TODO** Check side-effect.
* Serialization & Deserialization of the description
  + Convert description object to JSON string.
  + **TODO** Parse JSON string to get description object
